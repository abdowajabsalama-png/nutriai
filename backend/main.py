"""
NutriAI - Intelligent Personalized Diet Recommendation System
Backend: FastAPI with SQLite Database Persistence
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, List

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

import backend.database as db
from backend.providers.groq_provider import GroqProvider
from backend.providers.openai_provider import OpenAIProvider
from backend.providers.offline_provider import OfflineProvider

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("nutriai")

# ══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT
# ══════════════════════════════════════════════════════════════════════════════

load_dotenv()

GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
JWT_SECRET         = os.getenv("JWT_SECRET", "nutriai-secret-key-change-in-prod")
JWT_ALGORITHM      = "HS256"
JWT_EXPIRE_HOURS   = 48

# ══════════════════════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="NutriAI API",
    description="Personalized AI Diet Recommendation System with SQLite Persistence",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 ─ SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)
    email:    str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    age:             int
    gender:          str
    height_cm:       float
    weight_kg:       float
    activity_level:  str        # sedentary / light / moderate / active / very_active
    goal:            str        # lose_weight / maintain / gain_muscle

    # Medical
    diabetes:          bool = False
    hypertension:      bool = False
    high_cholesterol:  bool = False
    thyroid_disorder:  bool = False
    other_conditions:  Optional[str] = ""

    # Allergies & Intolerances
    allergies:           List[str] = []
    lactose_intolerance: bool = False
    gluten_intolerance:  bool = False
    other_intolerances:  Optional[str] = ""

    # Medications & Diet
    medications:   Optional[str] = ""
    diet_type:     str = "regular"   # keto / vegetarian / vegan / regular
    special_notes: Optional[str] = ""

class GeneratePlanRequest(BaseModel):
    session_id: str
    profile:    UserProfile
    provider:   str = "offline"   # offline | groq | openrouter
    language:   str = "ar"        # ar | en

class ChatRequest(BaseModel):
    session_id: str
    message:    str
    provider:   str = "offline"

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 ─ AUTH UTILITIES
# ══════════════════════════════════════════════════════════════════════════════

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return decode_token(credentials.credentials)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 ─ PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """\
You are a certified clinical nutrition assistant.

Your task is to generate a personalized 15-day meal plan based strictly on the user's structured health data.

Clinical Safety Rules:
- If Diabetes = yes: Limit simple sugars, prefer low glycemic index carbs, distribute carbs evenly.
- If Hypertension = yes: Limit sodium, avoid processed/canned foods, emphasize potassium-rich foods.
- If High Cholesterol = yes: Reduce saturated fats, avoid fried food, increase fiber.
- If Lactose intolerance: Avoid dairy, use lactose-free or plant alternatives.
- If Gluten intolerance: Avoid wheat, barley, rye — use gluten-free alternatives.
- Strictly exclude any listed allergy items.
- Never include food that conflicts with medical conditions.
- If medical case is complex, add a stronger medical disclaimer.

CRITICAL OUTPUT RULES:
- You MUST respond with ONLY a valid JSON object.
- Do NOT include any markdown, code fences, explanation, or text outside the JSON.
- Your entire response must start with { and end with }.
- Every string value must be properly quoted and escaped.
- Do NOT use single quotes; use double quotes only.
"""

def build_diet_user_prompt(p: UserProfile, language: str = "ar") -> str:
    allergies_str = ", ".join(p.allergies) if p.allergies else "None"

    lang_instruction = (
        "Language: ar\n"
        "LANGUAGE MANDATE: The user interface is Arabic. All values in the JSON (user_profile_summary, "
        "medical_adjustments items, meal descriptions, notes, and disclaimer) MUST be written in natural, professional Arabic. "
        "Keep the JSON object keys in English as specified in the schema.\n\n"
        if language == "ar" else
        "Language: en\n"
    )

    variables = (
        "{lang_instruction}"
        "User Data:\n"
        "Age: {age}\n"
        "Gender: {gender}\n"
        "Height: {height_cm} cm\n"
        "Weight: {weight_kg} kg\n"
        "Activity Level: {activity_level}\n"
        "Goal: {goal}\n"
        "\n"
        "Medical Conditions:\n"
        "- Diabetes: {diabetes}\n"
        "- Hypertension: {hypertension}\n"
        "- High Cholesterol: {high_cholesterol}\n"
        "- Thyroid Disorder: {thyroid_disorder}\n"
        "- Other Conditions: {other_conditions}\n"
        "\n"
        "Food Allergies: {allergies}\n"
        "\n"
        "Food Intolerances:\n"
        "- Lactose intolerance: {lactose}\n"
        "- Gluten intolerance: {gluten}\n"
        "- Other intolerances: {other_intolerances}\n"
        "\n"
        "Medications: {medications}\n"
        "Diet Preference: {diet_type}\n"
        "Special Notes: {special_notes}\n"
    ).format(
        lang_instruction   = lang_instruction,
        age                = p.age,
        gender             = p.gender,
        height_cm          = p.height_cm,
        weight_kg          = p.weight_kg,
        activity_level     = p.activity_level,
        goal               = p.goal,
        diabetes           = "yes" if p.diabetes           else "no",
        hypertension       = "yes" if p.hypertension       else "no",
        high_cholesterol   = "yes" if p.high_cholesterol   else "no",
        thyroid_disorder   = "yes" if p.thyroid_disorder   else "no",
        other_conditions   = p.other_conditions   or "None",
        allergies          = allergies_str,
        lactose            = "yes" if p.lactose_intolerance else "no",
        gluten             = "yes" if p.gluten_intolerance  else "no",
        other_intolerances = p.other_intolerances or "None",
        medications        = p.medications        or "None",
        diet_type          = p.diet_type,
        special_notes      = p.special_notes      or "None",
    )

    schema = """
Generate a complete 15-day meal plan as a JSON object matching this schema exactly.
Return ONLY the JSON object — no markdown, no code fences, no explanation.
Your entire response must start with { and end with }.

{
  "user_profile_summary": "string",
  "daily_calories": "string",
  "macros": { "protein": "string", "carbs": "string", "fat": "string" },
  "medical_adjustments": ["string"],
  "meal_plan": [
    {
      "day": "Day 1",
      "meals": {
        "breakfast": { "meal": "string", "calories": "string", "notes": "string" },
        "lunch":     { "meal": "string", "calories": "string", "notes": "string" },
        "dinner":    { "meal": "string", "calories": "string", "notes": "string" },
        "snack":     { "meal": "string", "calories": "string", "notes": "string" }
      }
    }
  ],
  "disclaimer": "string"
}

The meal_plan array MUST contain exactly 15 items (Day 1 through Day 15).
Respond with ONLY the JSON object. No other text.
"""

    return variables + schema


CHAT_SYSTEM_PROMPT = """\
You are NutriAI, an expert clinical nutrition assistant.
The user has a personalized 15-day diet plan.
Answer their questions about diet, nutrition, healthy cooking, ingredients, and substitutions.
Always reply in the same language the user uses (Arabic or English).
Keep answers concise, practical, motivating, and medically safe."""

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 ─ PROVIDER FACTORY
# ══════════════════════════════════════════════════════════════════════════════

def get_provider(name: str):
    if name == "offline":
        return OfflineProvider()
    elif name == "groq":
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not configured, falling back to OfflineProvider")
            return OfflineProvider()
        return GroqProvider(api_key=GROQ_API_KEY)
    elif name == "openrouter":
        if not OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY is not configured, falling back to OfflineProvider")
            return OfflineProvider()
        return OpenAIProvider(api_key=OPENROUTER_API_KEY)
    else:
        return OfflineProvider()

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 ─ JSON PARSER UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def parse_llm_json(raw: str) -> dict:
    clean = raw.strip()
    clean = clean.replace("{{", "{").replace("}}", "}")

    if "```json" in clean:
        clean = clean.split("```json", 1)[1].rsplit("```", 1)[0].strip()
    elif "```" in clean:
        clean = clean.split("```", 1)[1].rsplit("```", 1)[0].strip()

    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in response")

    clean = clean[start:end]

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        snippet = clean[max(0, e.pos - 60): e.pos + 60]
        raise ValueError(f"JSON decode error at pos {e.pos}: {e.msg}\n...{snippet}...")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 ─ AUTH ENDPOINTS (SQLite)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    existing = db.get_user(req.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    success = db.create_user(req.username, req.password, req.email)
    if not success:
        raise HTTPException(status_code=400, detail="Could not create user account")

    logger.info("Registered new user in SQLite: %s", req.username)
    return {"message": "User registered successfully"}


@app.post("/auth/login")
def login(req: LoginRequest):
    user = db.get_user(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(req.username)
    logger.info("User logged in: %s", req.username)
    return {"access_token": token, "token_type": "bearer", "username": req.username}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 ─ SESSION ENDPOINTS (SQLite)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/sessions/new")
def new_session(username: str = Depends(get_current_user)):
    session_id = str(uuid.uuid4())
    db.create_session(session_id, username)
    logger.info("Created new session in SQLite: %s for user %s", session_id, username)
    return {"session_id": session_id}


@app.get("/sessions")
def list_sessions(username: str = Depends(get_current_user)):
    user_sessions = db.list_user_sessions(username)
    return {"sessions": user_sessions}


@app.get("/sessions/{session_id}")
def get_session_detail(session_id: str, username: str = Depends(get_current_user)):
    session = db.get_session(session_id, username)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session["session_id"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "diet_plan":  session["diet_plan"],
        "history":    session["history"],
        "language":   session.get("language", "ar")
    }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str, username: str = Depends(get_current_user)):
    success = db.delete_session(session_id, username)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 ─ DIET PLAN GENERATION (SQLite)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/diet/generate")
async def generate_diet_plan(
    req: GeneratePlanRequest,
    username: str = Depends(get_current_user),
):
    session = db.get_session(req.session_id, username)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    logger.info("Generating diet plan: user=%s session=%s provider=%s lang=%s",
                username, req.session_id, req.provider, req.language)

    provider    = get_provider(req.provider)
    user_prompt = build_diet_user_prompt(req.profile, language=req.language)

    try:
        raw_response = await provider.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.2,
            max_tokens=16000,
        )
    except Exception as exc:
        logger.warning("Provider %s failed (%s), falling back to OfflineProvider", req.provider, exc)
        offline_p = OfflineProvider()
        raw_response = await offline_p.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    try:
        diet_plan = parse_llm_json(raw_response)
    except ValueError as e:
        logger.error("JSON parse failed: %s\nRaw:\n%s", e, raw_response)
        raise HTTPException(status_code=500, detail=f"Invalid diet plan format returned: {e}")

    if "meal_plan" not in diet_plan:
        raise HTTPException(status_code=500, detail="Generated plan missing 'meal_plan' property")

    # Persist diet plan directly to SQLite
    db.save_session_plan(req.session_id, diet_plan, language=req.language)

    # Initialize chat history in SQLite if empty
    existing_msgs = db.get_messages(req.session_id)
    if not existing_msgs:
        welcome_msg = (
            "لقد قمت بإعداد خطتك الغذائية المخصصة لـ 15 يوماً بنجاح! 🥗 يمكنك سؤالي عن أي استفسار أو بدائل غذائية."
            if req.language == "ar" else
            "I've generated your 15-day meal plan successfully! 🥗 Ask me anything about it!"
        )
        db.add_message(req.session_id, "system", CHAT_SYSTEM_PROMPT)
        db.add_message(req.session_id, "assistant", welcome_msg)

    logger.info("Diet plan saved in SQLite for session=%s", req.session_id)
    return {"diet_plan": diet_plan}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 ─ CHAT (Conversation Memory in SQLite)
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/chat")
async def chat(
    req: ChatRequest,
    username: str = Depends(get_current_user),
):
    session = db.get_session(req.session_id, username)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.get("diet_plan"):
        raise HTTPException(status_code=400, detail="Generate a diet plan first")

    # Save user message to SQLite
    db.add_message(req.session_id, "user", req.message)

    # Load messages
    all_msgs = db.get_messages(req.session_id)
    chat_payload = [{"role": m["role"], "content": m["content"]} for m in all_msgs]

    provider = get_provider(req.provider)
    active_plan = session.get("diet_plan")
    try:
        reply = await provider.chat_with_history(
            messages=chat_payload,
            diet_plan=active_plan,
            temperature=0.7,
        )
    except TypeError:
        reply = await provider.chat_with_history(
            messages=chat_payload,
            temperature=0.7,
        )
    except Exception as exc:
        logger.warning("Provider %s chat failed (%s), falling back to OfflineProvider", req.provider, exc)
        offline_p = OfflineProvider()
        reply = await offline_p.chat_with_history(
            messages=chat_payload,
            diet_plan=active_plan,
            temperature=0.7,
        )

    # Save assistant reply to SQLite
    db.add_message(req.session_id, "assistant", reply)
    if active_plan:
        db.save_session_plan(req.session_id, active_plan, language=session.get("language", "ar"))

    # Return updated history and updated plan
    updated_history = db.get_messages(req.session_id)
    return {
        "reply":     reply,
        "history":   [{"role": m["role"], "content": m["content"]} for m in updated_history],
        "diet_plan": active_plan,
    }


@app.get("/chat/history/{session_id}")
def get_history(session_id: str, username: str = Depends(get_current_user)):
    session = db.get_session(session_id, username)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = db.get_messages(session_id)
    return {"history": [{"role": m["role"], "content": m["content"]} for m in msgs]}

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 ─ HEALTH & DEFENSE STATS
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
def health():
    return {
        "status":    "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version":   "2.0.0",
        "database":  "sqlite3 (connected)",
        "providers": {
            "offline":    True,
            "groq":       bool(GROQ_API_KEY),
            "openrouter": bool(OPENROUTER_API_KEY),
        },
    }

@app.get("/admin/overview")
def admin_overview(username: str = Depends(get_current_user)):
    """Admin / Graduation Defense overview endpoint displaying database health and records."""
    users = db.get_all_users()
    sessions = db.list_user_sessions(username)
    return {
        "total_registered_users": len(users),
        "user_sessions_count": len(sessions),
        "users": users,
    }

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 ─ ENTRYPOINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
