# 🥗 NutriAI — Intelligent Personalized Clinical Diet Recommendation System

NutriAI is a comprehensive clinical AI nutrition platform that generates customized 15-day meal plans based on anthropometric health profiles, clinical conditions, food allergies, and dietary preferences. It features an interactive conversational nutrition assistant that dynamically adapts and updates the meal plan in real time, full SQLite database persistence, bilingual support (Arabic RTL & English), and clinical PDF export.

---

## ✨ Key Features

- **Personalized 15-Day Meal Plans:** Evidence-based meal schedules calculated via clinical Mifflin-St Jeor and TDEE equations.
- **Clinical Safety Rules:** Automatic recipe adjustments for Type-2 Diabetes, Hypertension, High Cholesterol, Thyroid disorders, Lactose intolerance, Gluten intolerance (Celiac), and specific food allergies.
- **Dynamic Multi-Provider AI Architecture:**
  - **⚡ Offline Engine (Default):** 100% local, evidence-based nutrition intelligence and conversational clinical assistant without requiring internet or external API keys.
  - **☁️ Groq Cloud:** High-speed cloud LLM inference powered by `llama-3.3-70b-versatile`.
  - **☁️ OpenRouter Cloud:** Flexible access to state-of-the-art models.
- **Real-Time Plan Customization via Chat:**
  - Conversational food substitutions (e.g. replacing chicken with fish or eggs with cottage cheese across all 15 days).
  - Natural language bilateral day swapping (e.g. swapping Day 1 with Day 2).
  - Immediate visual badges and live synchronizations with SQLite database and PDF exports.
- **Clinical PDF Export:** Generates formatted A4 PDF reports with full Arabic text shaping, bidirectional (RTL) flow, and nutritional macronutrient breakdowns.
- **Persistent SQLite Database:** Secure local storage for users, authentication tokens, 15-day plan sessions, and full conversation history in `data/nutriai.db`.
- **Modern Bilingual UI:** Arabic (RTL) and English (LTR) with dark and light themes built with Streamlit.

---

## 🏗️ Architecture

```
nutrial-ai/
├── backend/
│   ├── main.py                  # FastAPI REST API endpoints
│   ├── database.py              # SQLite relational persistence layer
│   └── providers/
│       ├── offline_provider.py  # Local clinical engine & NLP intent matching
│       ├── groq_provider.py     # Groq LPU API client
│       └── openai_provider.py   # OpenRouter API client
├── frontend/
│   ├── app.py                   # Streamlit bilingual user interface
│   └── pdf_export.py            # ReportLab Arabic clinical PDF generator
├── data/
│   └── nutriai.db               # SQLite database file
├── launcher.pyw                 # Background process supervisor
├── launch_nutriai.bat           # One-click portable launcher
├── stop_nutriai.bat             # Clean shutdown script
├── requirements.txt             # Complete python dependencies
└── README.md
```

---

## ⚡ Quickstart & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/nutriai.git
cd nutriai
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run NutriAI

#### Option A: One-Click Launcher (Windows)
Double-click `launch_nutriai.bat` in the project root. It will automatically start the backend and frontend and open your browser.

#### Option B: Manual Execution

In Terminal 1 (Backend):
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*API documentation available at:* `http://127.0.0.1:8000/docs`

In Terminal 2 (Frontend):
```bash
streamlit run frontend/app.py --server.port 8501
```
*Application available at:* `http://localhost:8501`

---

## 🔑 Optional Cloud Configuration (`.env`)

For offline operation, no configuration is required! To enable cloud models, create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
JWT_SECRET=your_secure_jwt_secret
```

---

## 📄 License
MIT License. Developed for clinical dietetics and evidence-based nutritional recommendation research.
