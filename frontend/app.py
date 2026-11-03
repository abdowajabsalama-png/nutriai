"""
NutriAI - Streamlit Frontend
Bilingual (Arabic / English) with Dark / Light Mode, Clean UI, and Real PDF Export
"""

import streamlit as st
import requests
import json
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG & PAGE SETUP
# ══════════════════════════════════════════════════════════════════════════════

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="NutriAI - Personalized Nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DICTIONARY FOR BILINGUAL LOCALIZATION
# ══════════════════════════════════════════════════════════════════════════════

T = {
    "ar": {
        "tagline": "نظام التغذية العلاجية الذكي المخصص",
        "login": "تسجيل الدخول",
        "register": "إنشاء حساب جديد",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "email": "البريد الإلكتروني",
        "login_btn": "تسجيل الدخول ←",
        "create_account": "إنشاء الحساب ←",
        "login_success": "تم تسجيل الدخول بنجاح!",
        "account_created": "تم إنشاء الحساب بنجاح! يرجى تسجيل الدخول.",
        "fill_all": "يرجى ملء جميع الحقول المطلوبة.",
        "theme": "المظهر / Theme",
        "dark": "🌙 الوضع الليلي (Dark)",
        "light": "☀️ الوضع المضيء (Light)",
        "language": "اللغة / Language",
        "lang_ar": "🇸🇦 العربية",
        "lang_en": "🇬🇧 English",
        "ai_provider": "محرك الذكاء الاصطناعي",
        "new_plan": "+ خطة غذائية جديدة",
        "previous_plans": "الخطط السابقة المحفوظة",
        "logout": "تسجيل الخروج",
        "profile_title": "ملفك الصحي والبدني",
        "profile_desc": "أدخل بياناتك بدقة لتوليد نظام غذائي مخصص وآمن طبياً لمدة 15 يوماً.",
        "age": "العمر (سنة)",
        "height": "الطول (سم)",
        "weight": "الوزن (كجم)",
        "gender": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "activity": "مستوى النشاط البدني",
        "act_sedentary": "🪑 قليل الحركة (عمل مكتبي)",
        "act_light": "🚶 نشاط خفيف (1-3 أيام/أسبوع)",
        "act_moderate": "🏃 نشاط متوسط (3-5 أيام/أسبوع)",
        "act_active": "💪 نشيط (6-7 أيام/أسبوع)",
        "act_very_active": "🔥 نشيط جداً (رياضي محترف)",
        "goal": "الهدف الصحي",
        "goal_lose": "⬇️ خسارة الوزن والدهون",
        "goal_maintain": "⚖️ تثبيت الوزن والمحافظة",
        "goal_muscle": "⬆️ زيادة الكتلة العضلية",
        "medical_header": "الحالات والأمراض الطبية",
        "diabetes": "🩸 مرض السكري",
        "hypertension": "❤️ ارتفاع ضغط الدم",
        "cholesterol": "🫀 ارتفاع الكوليسترول",
        "thyroid": "🦋 اضطراب الغدة الدرقية",
        "other_medical": "حالات أو أمراض أخرى",
        "allergies_header": "الحساسيات وعدم تحمل الأطعمة",
        "food_allergies": "الحساسيات الغذائية المعروفة",
        "other_allergies": "حساسيات طعام أخرى",
        "lactose": "🥛 عدم تحمل اللاكتوز (مشتقات الحليب)",
        "gluten": "🌾 عدم تحمل الجلوتين (القمح)",
        "other_intolerances": "أنواع عدم تحمل أخرى",
        "diet_meds_header": "النمط الغذائي والأدوية",
        "diet_pref": "النمط الغذائي المفضل",
        "diet_regular": "🍽️ متوازن وعادي",
        "diet_veg": "🥦 نباتي (Vegetarian)",
        "diet_vegan": "🌱 نباتي صرف (Vegan)",
        "diet_keto": "🥑 كيتو (Keto)",
        "medications": "الأدوية والمكملات الحالية",
        "special_notes": "ملاحظات وتفضيلات إضافية",
        "generate_btn": "🌿 إنشاء خطتي الغذائية لـ 15 يوماً",
        "analyzing": "🧠 جاري تحليل ملفك الصحي وتوليد الخطة المخصصة طبياً...",
        "plan_title": "خطتك الغذائية المخصصة لـ 15 يوماً",
        "cals_day": "سعرة / اليوم",
        "protein": "البروتين",
        "carbs": "الكربوهيدرات",
        "fat": "الدهون",
        "medical_notes": "التعديلات والاحتياطات الطبية المعتمدة",
        "breakfast": "الإفطار",
        "lunch": "الغداء",
        "dinner": "العشاء",
        "snack": "سناك",
        "chat_title": "المحادثة مع المساعد التغذوي الذكي",
        "chat_desc": "اسأل المساعد الذكي عن أي استفسار أو بدائل غذائية أو نصائح للطهي.",
        "chat_placeholder": "اكتب رسالتك أو استفسارك هنا...",
        "send": "إرسال ←",
        "clear": "مسح المحادثة",
        "you": "أنت",
        "assistant": "🥗 NutriAI المساعد الذكي",
        "no_plan": "لا توجد خطة محملة لهذه الجلسة.",
        "back_to_form": "← إنشاء خطة جديدة",
        "download_pdf": "📄 تحميل الخطة كملف PDF رسمي (15 يوماً)",
    },
    "en": {
        "tagline": "Personalized Clinical Nutrition",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "login_btn": "Login →",
        "create_account": "Create Account →",
        "login_success": "Logged in successfully!",
        "account_created": "Account created! Please login.",
        "fill_all": "Please fill all fields.",
        "theme": "Theme / المظهر",
        "dark": "🌙 Dark Mode",
        "light": "☀️ Light Mode",
        "language": "Language / اللغة",
        "lang_ar": "🇸🇦 Arabic",
        "lang_en": "🇬🇧 English",
        "ai_provider": "AI Provider",
        "new_plan": "+ New Diet Plan",
        "previous_plans": "Saved Previous Plans",
        "logout": "Logout",
        "profile_title": "Your Health Profile",
        "profile_desc": "Fill in your details to generate a medically safe, personalized 15-day meal plan.",
        "age": "Age",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "gender": "Gender",
        "male": "Male",
        "female": "Female",
        "activity": "Activity Level",
        "act_sedentary": "🪑 Sedentary (desk job)",
        "act_light": "🚶 Light (1-3 days/week)",
        "act_moderate": "🏃 Moderate (3-5 days/week)",
        "act_active": "💪 Active (6-7 days/week)",
        "act_very_active": "🔥 Very Active (athlete)",
        "goal": "Goal",
        "goal_lose": "⬇️ Lose Weight",
        "goal_maintain": "⚖️ Maintain Weight",
        "goal_muscle": "⬆️ Gain Muscle",
        "medical_header": "Medical Conditions",
        "diabetes": "🩸 Diabetes",
        "hypertension": "❤️ Hypertension",
        "cholesterol": "🫀 High Cholesterol",
        "thyroid": "🦋 Thyroid Disorder",
        "other_medical": "Other medical conditions",
        "allergies_header": "Allergies & Intolerances",
        "food_allergies": "Food Allergies",
        "other_allergies": "Other food allergies",
        "lactose": "🥛 Lactose Intolerance",
        "gluten": "🌾 Gluten Intolerance",
        "other_intolerances": "Other intolerances",
        "diet_meds_header": "Diet & Medications",
        "diet_pref": "Diet Preference",
        "diet_regular": "🍽️ Regular",
        "diet_veg": "🥦 Vegetarian",
        "diet_vegan": "🌱 Vegan",
        "diet_keto": "🥑 Keto",
        "medications": "Current Medications",
        "special_notes": "Special Notes",
        "generate_btn": "🌿 Generate My 15-Day Meal Plan",
        "analyzing": "🧠 Analyzing your health profile and generating your clinical plan...",
        "plan_title": "Your Personalized 15-Day Plan",
        "cals_day": "Calories / Day",
        "protein": "Protein",
        "carbs": "Carbs",
        "fat": "Fat",
        "medical_notes": "Clinical Adjustments & Precautions",
        "breakfast": "Breakfast",
        "lunch": "Lunch",
        "dinner": "Dinner",
        "snack": "Snack",
        "chat_title": "Chat with NutriAI Assistant",
        "chat_desc": "Ask anything about your meal plan, substitutions, or cooking tips.",
        "chat_placeholder": "Type your message or question here...",
        "send": "Send →",
        "clear": "Clear",
        "you": "You",
        "assistant": "🥗 NutriAI Assistant",
        "no_plan": "No meal plan loaded for this session.",
        "back_to_form": "← Create New Plan",
        "download_pdf": "📄 Download Official Meal Plan (PDF)",
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC CSS (Dark / Light Theme + RTL / LTR Support)
# ══════════════════════════════════════════════════════════════════════════════

def inject_styles(theme: str, lang: str):
    is_ar = (lang == "ar")
    is_dark = (theme == "dark")

    direction   = "rtl" if is_ar else "ltr"
    text_align  = "right" if is_ar else "left"
    margin_side = "margin-right" if is_ar else "margin-left"

    if is_dark:
        bg_main       = "#0f1117"
        bg_sidebar    = "#13191a"
        bg_card       = "#13191a"
        bg_day        = "#111a11"
        bg_input      = "#13191a"
        text_color    = "#e8e8e0"
        label_color   = "#d8e4d8"
        text_muted    = "#7a9a7a"
        border_color  = "#1e3a1e"
        accent_color  = "#a8d5a2"
        badge_cal     = "#4a7a4a"
        chat_user_bg  = "#1a2e1a"
        chat_user_brd = "#2a4a2a"
        chat_user_txt = "#d0e8d0"
        chat_bot_bg   = "#131a13"
        chat_bot_brd  = "#1e2e1e"
        chat_bot_txt  = "#b0c8b0"
        disc_bg       = "#1a1510"
        disc_brd      = "#3a2a10"
        disc_txt      = "#8a7a50"
    else:
        bg_main       = "#f8faf8"
        bg_sidebar    = "#ffffff"
        bg_card       = "#ffffff"
        bg_day        = "#ffffff"
        bg_input      = "#ffffff"
        text_color    = "#111827"
        label_color   = "#111827"
        text_muted    = "#374151"
        border_color  = "#cbd5e1"
        accent_color  = "#15803d"
        badge_cal     = "#16a34a"
        chat_user_bg  = "#e8f5e9"
        chat_user_brd = "#c8e6c9"
        chat_user_txt = "#1b5e20"
        chat_bot_bg   = "#f1f5f9"
        chat_bot_brd  = "#cbd5e1"
        chat_bot_txt  = "#1e293b"
        disc_bg       = "#fffbeb"
        disc_brd      = "#fde68a"
        disc_txt      = "#92400e"

    day_border = f"border-right: 4px solid #16a34a; border-radius: 8px 0 0 8px;" if is_ar else f"border-left: 4px solid #16a34a; border-radius: 0 8px 8px 0;"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=DM+Sans:wght@300;400;500;700&family=Playfair+Display:wght@600;700&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
        font-family: {'"Cairo", ' if is_ar else ''}'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: {bg_main};
        color: {text_color};
        direction: {direction};
        text-align: {text_align};
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1.5rem; }}

    /* ── Hide 'Press Enter to apply' helper instructions completely ── */
    div[data-testid="InputInstructions"],
    [data-testid="InputInstructions"],
    .stTextInput small,
    .stNumberInput small,
    .stTextArea small,
    small {{
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        max-height: 0 !important;
        font-size: 0 !important;
        line-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        opacity: 0 !important;
    }}

    [data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        border-{'left' if is_ar else 'right'}: 1px solid {border_color} !important;
    }}
    [data-testid="stSidebar"] .block-container {{ padding: 1.5rem 1rem; }}

    /* ── High-Specificity Labels Fix for Light & Dark Mode ── */
    label,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stMultiSelect label,
    .stTextArea label,
    .stCheckbox label span,
    .stRadio label,
    .stRadio label span,
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] span,
    .stTabs [data-baseweb="tab"] p,
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] span,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4,
    div[data-testid="stCaptionContainer"] p {{
        color: {label_color} !important;
        font-weight: 600 !important;
    }}

    /* ── Inputs Styling & Wrappers (Prevent dark background when typing) ── */
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"],
    .stTextInput > div > div,
    .stNumberInput > div > div,
    .stTextArea > div > div {{
        background-color: {bg_input} !important;
        border-color: {border_color} !important;
        color: {text_color} !important;
        border-radius: 6px !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stSelectbox select,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div {{
        background-color: {bg_input} !important;
        border: 1.5px solid {border_color} !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        border-radius: 6px !important;
        text-align: {text_align} !important;
        direction: {direction} !important;
    }}

    /* Focus state */
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {{
        border-color: #16a34a !important;
        box-shadow: 0 0 0 1px #16a34a !important;
    }}

    /* ── Checkboxes (Fix black box in Light Mode) ── */
    div[data-testid="stCheckbox"] {{
        background-color: transparent !important;
    }}
    div[data-testid="stCheckbox"] label {{
        color: {label_color} !important;
    }}
    div[data-baseweb="checkbox"] {{
        background-color: transparent !important;
    }}
    div[data-baseweb="checkbox"] > div:first-child,
    div[data-baseweb="checkbox"] span:first-child {{
        background-color: {'#1e293b' if is_dark else '#ffffff'} !important;
        border: 2px solid {'#4ade80' if is_dark else '#cbd5e1'} !important;
        border-radius: 4px !important;
    }}
    div[data-baseweb="checkbox"]:hover > div:first-child,
    div[data-baseweb="checkbox"]:hover span:first-child {{
        border-color: #16a34a !important;
    }}
    div[data-baseweb="checkbox"] input:checked + div,
    div[data-baseweb="checkbox"] input:checked ~ div,
    div[data-baseweb="checkbox"] input:checked + span,
    div[data-baseweb="checkbox"] input:checked ~ span {{
        background-color: #16a34a !important;
        border-color: #16a34a !important;
    }}
    div[data-baseweb="checkbox"] svg {{
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }}

    /* Stepper buttons for number inputs */
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {{
        color: {text_color} !important;
        background-color: {bg_day} !important;
    }}

    /* Multiselect tags */
    [data-baseweb="tag"] {{
        background-color: {'#2a4a2a' if is_dark else '#e2e8f0'} !important;
        color: {'#d0e8d0' if is_dark else '#1e293b'} !important;
        border-radius: 4px !important;
    }}

    .nutriai-logo {{
        font-family: {'"Cairo", ' if is_ar else ''}'Playfair Display', Georgia, serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: {accent_color};
        margin-bottom: 0.2rem;
    }}
    .nutriai-tagline {{
        font-size: 0.78rem;
        color: {text_muted};
        letter-spacing: {'0.5px' if is_ar else '2px'};
        text-transform: {'none' if is_ar else 'uppercase'};
        margin-bottom: 1.2rem;
    }}

    .section-header {{
        font-family: {'"Cairo", ' if is_ar else ''}'Playfair Display', serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: {accent_color};
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid {border_color};
    }}

    .info-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 1rem;
        box-shadow: {'0 2px 8px rgba(0,0,0,0.04)' if not is_dark else 'none'};
        color: {text_color};
    }}

    .day-card {{
        background: {bg_day};
        {day_border}
        border-top: 1px solid {border_color};
        border-bottom: 1px solid {border_color};
        border-{'left' if is_ar else 'right'}: 1px solid {border_color};
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.8rem;
        box-shadow: {'0 2px 6px rgba(0,0,0,0.03)' if not is_dark else 'none'};
    }}
    .day-title {{
        font-family: {'"Cairo", ' if is_ar else ''}'Playfair Display', serif;
        color: {accent_color};
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}

    .meal-row {{
        display: flex;
        gap: 0.6rem;
        align-items: baseline;
        margin-bottom: 0.35rem;
        font-size: 0.86rem;
    }}
    .meal-label {{
        color: {accent_color};
        font-weight: 600;
        min-width: 85px;
        font-size: 0.76rem;
        text-transform: {'none' if is_ar else 'uppercase'};
        letter-spacing: 0.5px;
    }}
    .meal-text {{
        color: {text_color};
        flex: 1;
    }}
    .meal-cal {{
        color: {badge_cal};
        font-size: 0.76rem;
        font-weight: 600;
        white-space: nowrap;
        {margin_side}: auto;
    }}

    .macro-bar {{
        display: flex;
        gap: 0.8rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }}
    .macro-item {{
        flex: 1;
        min-width: 120px;
        background: {bg_day};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        box-shadow: {'0 2px 6px rgba(0,0,0,0.03)' if not is_dark else 'none'};
    }}
    .macro-value {{
        font-family: {'"Cairo", ' if is_ar else ''}'Playfair Display', serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: {accent_color};
    }}
    .macro-label {{
        font-size: 0.75rem;
        color: {text_muted};
        font-weight: 600;
        margin-top: 0.2rem;
    }}

    .chat-user {{
        background: {chat_user_bg};
        border: 1px solid {chat_user_brd};
        border-radius: 12px 12px { '12px 2px' if is_ar else '2px 12px' };
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 0.5rem { '0' if is_ar else '15%' };
        {margin_side}: { '15%' if is_ar else '0' };
        font-size: 0.9rem;
        color: {chat_user_txt};
    }}
    .chat-bot {{
        background: {chat_bot_bg};
        border: 1px solid {chat_bot_brd};
        border-radius: 12px 12px { '2px 12px' if is_ar else '12px 2px' };
        padding: 0.75rem 1rem;
        margin: 0.5rem 0 0.5rem { '15%' if is_ar else '0' };
        {margin_side}: { '0' if is_ar else '15%' };
        font-size: 0.9rem;
        color: {chat_bot_txt};
    }}
    .chat-label {{
        font-size: 0.7rem;
        font-weight: 700;
        color: {accent_color};
        margin-bottom: 0.25rem;
        letter-spacing: 0.5px;
    }}

    /* ── Buttons & Download Button (Fix dark/black box in Light Mode) ── */
    .stButton > button,
    .stDownloadButton > button,
    div[data-testid="stDownloadButton"] > button,
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="stBaseButton-primary"] {{
        background: { '#1b5e20' if is_dark else '#16a34a' } !important;
        color: #ffffff !important;
        border: 1px solid { '#2e7d32' if is_dark else '#15803d' } !important;
        border-radius: 8px !important;
        font-family: {'"Cairo", ' if is_ar else ''}'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    div[data-testid="stDownloadButton"] > button:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {{
        background: { '#2e7d32' if is_dark else '#15803d' } !important;
        border-color: { '#388e3c' if is_dark else '#166534' } !important;
        color: #ffffff !important;
    }}
    div[data-testid="stDownloadButton"] {{
        background-color: transparent !important;
    }}

    .disclaimer {{
        background: {disc_bg};
        border: 1px solid {disc_brd};
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-size: 0.82rem;
        color: {disc_txt};
        margin-top: 1rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        "token":        None,
        "username":     None,
        "session_id":   None,
        "sessions":     [],
        "diet_plan":    None,
        "chat_history": [],
        "page":         "auth",
        "provider":     "offline",
        "lang":         "ar",
        "theme":        "dark",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════════════════════════════
# API HELPERS
# ══════════════════════════════════════════════════════════════════════════════

_DIRECT_CLIENT = None
_USE_LOCAL_HTTP = None
def _is_local_http():
    global _USE_LOCAL_HTTP
    if _USE_LOCAL_HTTP is None:
        try:
            r = requests.get(f"{BACKEND_URL}/docs", timeout=0.2)
            _USE_LOCAL_HTTP = (r.status_code == 200)
        except Exception:
            _USE_LOCAL_HTTP = False
    return _USE_LOCAL_HTTP

def _get_direct_client():
    global _DIRECT_CLIENT
    if _DIRECT_CLIENT is None:
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from backend.main import app as _backend_app
        from starlette.testclient import TestClient
        _DIRECT_CLIENT = TestClient(_backend_app, raise_server_exceptions=False)
    return _DIRECT_CLIENT

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def api_post(path, payload, auth=False):
    headers = auth_headers() if auth else {}
    if _is_local_http():
        try:
            r = requests.post(f"{BACKEND_URL}{path}", json=payload, headers=headers, timeout=60)
            return r.json(), r.status_code
        except Exception:
            pass
    try:
        r = _get_direct_client().post(path, json=payload, headers=headers)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": f"Error: {e}"}, 503

def api_get(path, auth=True):
    headers = auth_headers() if auth else {}
    if _is_local_http():
        try:
            r = requests.get(f"{BACKEND_URL}{path}", headers=headers, timeout=15)
            return r.json(), r.status_code
        except Exception:
            pass
    try:
        r = _get_direct_client().get(path, headers=headers)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": f"Error: {e}"}, 503

def api_delete(path):
    headers = auth_headers()
    if _is_local_http():
        try:
            r = requests.delete(f"{BACKEND_URL}{path}", headers=headers, timeout=10)
            return r.json(), r.status_code
        except Exception:
            pass
    try:
        r = _get_direct_client().delete(path, headers=headers)
        return r.json(), r.status_code
    except Exception as e:
        return {"detail": f"Error: {e}"}, 503

def _load_sessions():
    data, code = api_get("/sessions")
    if code == 200:
        st.session_state.sessions = data.get("sessions", [])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 - AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════

def render_auth():
    t = T[st.session_state.lang]
    inject_styles(st.session_state.theme, st.session_state.lang)

    # Top Controls for Auth Page (Theme & Language)
    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        lang_choice = st.radio(
            t["language"],
            ["ar", "en"],
            index=0 if st.session_state.lang == "ar" else 1,
            format_func=lambda x: t["lang_ar"] if x == "ar" else t["lang_en"],
            horizontal=True,
            key="auth_lang_radio",
        )
        if lang_choice != st.session_state.lang:
            st.session_state.lang = lang_choice
            st.rerun()

    with col_t2:
        theme_choice = st.radio(
            t["theme"],
            ["dark", "light"],
            index=0 if st.session_state.theme == "dark" else 1,
            format_func=lambda x: t["dark"] if x == "dark" else t["light"],
            horizontal=True,
            key="auth_theme_radio",
        )
        if theme_choice != st.session_state.theme:
            st.session_state.theme = theme_choice
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(f'<div class="nutriai-logo">🥗 NutriAI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nutriai-tagline">{t["tagline"]}</div>', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs([t["login"], t["register"]])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            # Clean fields without any transparent placeholders
            username = st.text_input(t["username"], key="login_user")
            password = st.text_input(t["password"], type="password", key="login_pass")
            if st.button(t["login_btn"], use_container_width=True):
                if not username or not password:
                    st.error(t["fill_all"])
                else:
                    data, code = api_post("/auth/login", {"username": username, "password": password})
                    if code == 200:
                        st.session_state.token    = data["access_token"]
                        st.session_state.username = username
                        st.session_state.page     = "form"
                        _load_sessions()
                        st.rerun()
                    else:
                        st.error(data.get("detail", "فشل تسجيل الدخول / Login failed"))

        with tab_register:
            st.markdown("<br>", unsafe_allow_html=True)
            # Clean registration fields without transparent placeholders
            r_user  = st.text_input(t["username"], key="reg_user")
            r_email = st.text_input(t["email"],    key="reg_email")
            r_pass  = st.text_input(t["password"], type="password", key="reg_pass")
            if st.button(t["create_account"], use_container_width=True):
                if not r_user or not r_email or not r_pass:
                    st.error(t["fill_all"])
                else:
                    data, code = api_post("/auth/register", {"username": r_user, "email": r_email, "password": r_pass})
                    if code == 201:
                        st.success(t["account_created"])
                    else:
                        st.error(data.get("detail", "فشل إنشاء الحساب / Registration failed"))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 - SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    t = T[st.session_state.lang]

    with st.sidebar:
        st.markdown('<div class="nutriai-logo" style="font-size:1.4rem">🥗 NutriAI</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="nutriai-tagline">@{st.session_state.username}</div>', unsafe_allow_html=True)

        # ── Language & Theme Controls ──
        c_lang, c_thm = st.columns(2)
        with c_lang:
            lang_choice = st.selectbox(
                "🌐",
                ["ar", "en"],
                index=0 if st.session_state.lang == "ar" else 1,
                format_func=lambda x: "🇸🇦 العربية" if x == "ar" else "🇬🇧 English",
                key="sb_lang_sel",
            )
            if lang_choice != st.session_state.lang:
                st.session_state.lang = lang_choice
                st.rerun()

        with c_thm:
            theme_choice = st.selectbox(
                "🎨",
                ["dark", "light"],
                index=0 if st.session_state.theme == "dark" else 1,
                format_func=lambda x: "🌙 داكن" if x == "dark" else "☀️ فاتح",
                key="sb_thm_sel",
            )
            if theme_choice != st.session_state.theme:
                st.session_state.theme = theme_choice
                st.rerun()

        st.divider()

        # ── AI Provider Selectbox ──
        provider_options = ["offline", "groq", "openrouter"]
        current_idx = provider_options.index(st.session_state.provider) if st.session_state.provider in provider_options else 0
        st.session_state.provider = st.selectbox(
            t["ai_provider"],
            provider_options,
            index=current_idx,
            format_func=lambda p: {
                "offline": "⚡ محرك محلي بدون إنترنت (Offline)",
                "groq": "سحابة Groq Cloud (Llama 3.3)",
                "openrouter": "سحابة OpenRouter Cloud",
            }.get(p, p) if st.session_state.lang == "ar" else {
                "offline": "⚡ Offline Engine (No Internet)",
                "groq": "Groq Cloud (Llama 3.3)",
                "openrouter": "OpenRouter Cloud",
            }.get(p, p),
        )

        st.divider()

        # ── New Diet Plan Button ──
        if st.button(t["new_plan"], use_container_width=True):
            data, code = api_post("/sessions/new", {}, auth=True)
            if code == 200:
                st.session_state.session_id   = data["session_id"]
                st.session_state.diet_plan    = None
                st.session_state.chat_history = []
                st.session_state.page         = "form"
                _load_sessions()
                st.rerun()
            else:
                st.error("تعذر إنشاء جلسة جديدة / Could not create session")

        # ── Previous Plans List (Restores both plan and chat from SQLite) ──
        st.markdown(f"**{t['previous_plans']}**")
        _load_sessions()

        if not st.session_state.sessions:
            st.caption("لا توجد خطط سابقة محفوظة بعد." if st.session_state.lang == "ar" else "No saved previous plans yet.")

        for s in st.session_state.sessions:
            sid     = s["session_id"]
            created = s["created_at"][:10]
            has_p   = s.get("has_plan", False)
            icon    = "🥗" if has_p else "📝"

            col_pill, col_del = st.columns([5, 1])
            with col_pill:
                btn_lbl = f"{icon} {created} ({sid[-4:]})"
                if st.button(btn_lbl, key=f"sess_{sid}", use_container_width=True):
                    # Fetch full session data including diet_plan and messages
                    data, code = api_get(f"/sessions/{sid}")
                    if code == 200:
                        st.session_state.session_id   = sid
                        st.session_state.diet_plan    = data.get("diet_plan")
                        st.session_state.chat_history = [
                            m for m in data.get("history", []) if m["role"] != "system"
                        ]
                        st.session_state.page = "chat" if st.session_state.diet_plan else "form"
                        st.rerun()
            with col_del:
                if st.button("✕", key=f"del_{sid}"):
                    api_delete(f"/sessions/{sid}")
                    if st.session_state.session_id == sid:
                        st.session_state.session_id   = None
                        st.session_state.diet_plan    = None
                        st.session_state.chat_history = []
                        st.session_state.page         = "form"
                    _load_sessions()
                    st.rerun()

        st.divider()

        # Clean sidebar logout button (database box removed as requested)
        if st.button(t["logout"], use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_state()
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 - DIET PROFILE FORM
# ══════════════════════════════════════════════════════════════════════════════

def render_form():
    t = T[st.session_state.lang]

    st.markdown(f'<div class="section-header">{t["profile_title"]}</div>', unsafe_allow_html=True)
    st.markdown(t["profile_desc"])
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    age    = c1.number_input(t["age"],    min_value=10,  max_value=100, value=30)
    height = c2.number_input(t["height"], min_value=100, max_value=250, value=170)
    weight = c3.number_input(t["weight"], min_value=30,  max_value=300, value=75)
    gender = c4.selectbox(t["gender"], ["Male", "Female"], format_func=lambda g: t["male"] if g == "Male" else t["female"])

    c5, c6 = st.columns(2)
    activity = c5.selectbox(
        t["activity"],
        ["sedentary", "light", "moderate", "active", "very_active"],
        format_func=lambda x: {
            "sedentary":   t["act_sedentary"],
            "light":       t["act_light"],
            "moderate":    t["act_moderate"],
            "active":      t["act_active"],
            "very_active": t["act_very_active"],
        }[x]
    )
    goal = c6.selectbox(
        t["goal"],
        ["lose_weight", "maintain", "gain_muscle"],
        format_func=lambda x: {
            "lose_weight": t["goal_lose"],
            "maintain":    t["goal_maintain"],
            "gain_muscle": t["goal_muscle"],
        }[x]
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-header" style="font-size:1.1rem">{t["medical_header"]}</div>', unsafe_allow_html=True)
    mc1, mc2, mc3, mc4 = st.columns(4)
    diabetes         = mc1.checkbox(t["diabetes"])
    hypertension     = mc2.checkbox(t["hypertension"])
    high_cholesterol = mc3.checkbox(t["cholesterol"])
    thyroid          = mc4.checkbox(t["thyroid"])
    # Clean input without transparent placeholder
    other_conditions = st.text_input(t["other_medical"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-header" style="font-size:1.1rem">{t["allergies_header"]}</div>', unsafe_allow_html=True)
    allergies_options = [
        "المكسرات (Nuts)", "المأكولات البحرية (Shellfish)", "البيض (Eggs)",
        "الصويا (Soy)", "الأسماك (Fish)", "السمسم (Sesame)", "الفول السوداني (Peanuts)"
    ] if st.session_state.lang == "ar" else ["Nuts", "Shellfish", "Eggs", "Soy", "Fish", "Sesame", "Peanuts"]

    allergies = st.multiselect(t["food_allergies"], allergies_options)
    custom_allergy = st.text_input(t["other_allergies"])
    if custom_allergy:
        allergies += [a.strip() for a in custom_allergy.split(",")]

    il1, il2 = st.columns(2)
    lactose = il1.checkbox(t["lactose"])
    gluten  = il2.checkbox(t["gluten"])
    other_intolerances = st.text_input(t["other_intolerances"])

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-header" style="font-size:1.1rem">{t["diet_meds_header"]}</div>', unsafe_allow_html=True)
    d1, d2 = st.columns(2)
    diet_type = d1.selectbox(
        t["diet_pref"],
        ["regular", "vegetarian", "vegan", "keto"],
        format_func=lambda x: {
            "regular":    t["diet_regular"],
            "vegetarian": t["diet_veg"],
            "vegan":      t["diet_vegan"],
            "keto":       t["diet_keto"],
        }[x]
    )
    medications   = d2.text_input(t["medications"])
    special_notes = st.text_area(t["special_notes"], height=80)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t["generate_btn"], use_container_width=True):
        if not st.session_state.session_id:
            data, code = api_post("/sessions/new", {}, auth=True)
            if code != 200:
                st.error("تعذر إنشاء الجلسة / Could not create session")
                return
            st.session_state.session_id = data["session_id"]

        profile = {
            "age": age, "gender": gender.lower(),
            "height_cm": height, "weight_kg": weight,
            "activity_level": activity, "goal": goal,
            "diabetes": diabetes, "hypertension": hypertension,
            "high_cholesterol": high_cholesterol, "thyroid_disorder": thyroid,
            "other_conditions": other_conditions, "allergies": allergies,
            "lactose_intolerance": lactose, "gluten_intolerance": gluten,
            "other_intolerances": other_intolerances,
            "medications": medications, "diet_type": diet_type,
            "special_notes": special_notes,
        }

        with st.spinner(t["analyzing"]):
            data, code = api_post("/diet/generate", {
                "session_id": st.session_state.session_id,
                "profile":    profile,
                "provider":   st.session_state.provider,
                "language":   st.session_state.lang,
            }, auth=True)

        if code == 200:
            st.session_state.diet_plan = data["diet_plan"]
            # Fetch newly initialized assistant message
            hist_data, _ = api_get(f"/chat/history/{st.session_state.session_id}")
            st.session_state.chat_history = [
                m for m in hist_data.get("history", []) if m["role"] != "system"
            ]
            st.session_state.page = "chat"
            _load_sessions()
            st.rerun()
        else:
            st.error(f"Error: {data.get('detail', 'Generation failed')}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 - DIET PLAN DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

def render_diet_plan(plan: dict):
    t = T[st.session_state.lang]

    st.markdown(f'<div class="section-header">{t["plan_title"]}</div>', unsafe_allow_html=True)

    summary_text = plan.get("user_profile_summary", "")
    if summary_text:
        st.markdown(f'<div class="info-card"><b>📌</b> {summary_text}</div>', unsafe_allow_html=True)

    macros = plan.get("macros", {})
    daily_cal = plan.get("daily_calories", "—")
    st.markdown(
        f'<div class="macro-bar">'
        f'<div class="macro-item"><div class="macro-value">{daily_cal}</div><div class="macro-label">{t["cals_day"]}</div></div>'
        f'<div class="macro-item"><div class="macro-value">{macros.get("protein", "—")}</div><div class="macro-label">{t["protein"]}</div></div>'
        f'<div class="macro-item"><div class="macro-value">{macros.get("carbs", "—")}</div><div class="macro-label">{t["carbs"]}</div></div>'
        f'<div class="macro-item"><div class="macro-value">{macros.get("fat", "—")}</div><div class="macro-label">{t["fat"]}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    adjustments = plan.get("medical_adjustments", [])
    if adjustments:
        adj_html = "<br>".join(["• " + a for a in adjustments])
        st.markdown(
            f'<div class="info-card" style="font-size:0.88rem; color:#2e7d32; font-weight:600; line-height:1.6;">'
            f'<b>{t["medical_notes"]}:</b><br>{adj_html}</div>',
            unsafe_allow_html=True,
        )

    meal_plan = plan.get("meal_plan", [])
    if meal_plan:
        left_html  = ""
        right_html = ""

        meal_labels = {
            "breakfast": t["breakfast"],
            "lunch":     t["lunch"],
            "dinner":    t["dinner"],
            "snack":     t["snack"],
        }

        for i, day_data in enumerate(meal_plan):
            meals     = day_data.get("meals", {})
            day_title = day_data.get("day", f"اليوم {i + 1}" if st.session_state.lang == "ar" else f"Day {i + 1}")

            meals_html = ""
            for meal_key in ["breakfast", "lunch", "dinner", "snack"]:
                m = meals.get(meal_key, {})
                if m:
                    label = meal_labels.get(meal_key, meal_key)
                    cal_str = m.get("calories", "")
                    note_str = m.get("notes", "")
                    note_badge = f'<br><span style="font-size:0.75rem; color:#2e7d32; font-weight:bold; background:rgba(46,125,50,0.12); padding:2px 8px; border-radius:4px; display:inline-block; margin-top:3px;">✨ {note_str}</span>' if (note_str and any(k in note_str for k in ["طلبك", "استبدال", "معدل", "تبديل"])) else ""
                    meals_html += (
                        f'<div class="meal-row">'
                        f'<span class="meal-label">{label}</span>'
                        f'<span class="meal-text">{m.get("meal", "")}{note_badge}</span>'
                        f'<span class="meal-cal">{cal_str}</span>'
                        f'</div>'
                    )

            card = f'<div class="day-card"><div class="day-title">{day_title}</div>{meals_html}</div>'

            if i % 2 == 0:
                left_html += card
            else:
                right_html += card

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(left_html,  unsafe_allow_html=True)
        with col_right:
            st.markdown(right_html, unsafe_allow_html=True)



    st.markdown("<br>", unsafe_allow_html=True)

    # ── Official PDF Download Button (Generates a clean clinical PDF, not raw code) ──
    try:
        from frontend.pdf_export import generate_diet_pdf
        pdf_data = generate_diet_pdf(plan, username=st.session_state.username or "User", language=st.session_state.lang)
        st.download_button(
            label=t["download_pdf"],
            data=pdf_data,
            file_name=f"NutriAI_Diet_Plan_{st.session_state.username}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as err:
        st.error(f"خطأ أثناء توليد ملف PDF: {err}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 - CHAT INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def render_chat():
    t = T[st.session_state.lang]

    if st.session_state.diet_plan:
        render_diet_plan(st.session_state.diet_plan)
    else:
        st.info(t["no_plan"])
        if st.button(t["back_to_form"]):
            st.session_state.page = "form"
            st.rerun()

    st.divider()

    st.markdown(f'<div class="section-header">{t["chat_title"]}</div>', unsafe_allow_html=True)
    st.markdown(t["chat_desc"])

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user"><div class="chat-label">{t["you"]}</div>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f'<div class="chat-bot"><div class="chat-label">{t["assistant"]}</div>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick Suggestion Chips ──
    suggested_prompts = [
        ("💡 وجبات اليوم الأول", "وجبات اليوم الأول إيه في خطتي؟") if st.session_state.lang == "ar" else ("💡 Day 1 Meals", "What are my Day 1 meals?"),
        ("🥩 احتياجي من البروتين", "البروتين محدد بكام جرام في خطتي؟") if st.session_state.lang == "ar" else ("🥩 Protein Target", "How much protein is in my plan?"),
        ("🍗 بدائل صدور الدجاج", "ممكن أبدل الفراخ بإيه لو مش عايز دجاج؟") if st.session_state.lang == "ar" else ("🍗 Chicken Substitutes", "What can I replace chicken breast with?"),
        ("☕ هل القهوة مسموحة؟", "هو أنا ممكن أشرب قهوة في الدايت؟") if st.session_state.lang == "ar" else ("☕ Coffee in Diet", "Can I drink coffee on this diet?"),
    ]

    col_chips = st.columns(len(suggested_prompts))
    for idx, (label_chip, prompt_text) in enumerate(suggested_prompts):
        with col_chips[idx]:
            if st.button(label_chip, key=f"chip_{idx}", use_container_width=True):
                with st.spinner("..."):
                    data, code = api_post("/chat", {
                        "session_id": st.session_state.session_id,
                        "message":    prompt_text,
                        "provider":   st.session_state.provider,
                    }, auth=True)
                if code == 200:
                    st.session_state.chat_history = [
                        m for m in data.get("history", []) if m["role"] != "system"
                    ]
                    if data.get("diet_plan"):
                        st.session_state.diet_plan = data["diet_plan"]
                        st.toast("✅ تم تحديث جداول الخطة الغذائية فوراً!", icon="🥗")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Interactive Form Chat Input (Press Enter or click Send, clears automatically) ──
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Chat Input",
            placeholder="اكتب استفسارك هنا واضغط Enter... (مثال: هل يمكن استبدال الأرز بالبطاطا؟)" if st.session_state.lang == "ar" else "Type your question and press Enter...",
            label_visibility="collapsed",
        )
        c_send, c_clear = st.columns([4, 1])
        with c_send:
            submitted = st.form_submit_button(t["send"], use_container_width=True)
        with c_clear:
            clear_btn = st.form_submit_button(t["clear"], use_container_width=True)

        if submitted and user_input.strip():
            if not st.session_state.session_id:
                st.error("لا توجد جلسة نشطة / No active session.")
            else:
                with st.spinner("🧠 NutriAI..."):
                    data, code = api_post("/chat", {
                        "session_id": st.session_state.session_id,
                        "message":    user_input.strip(),
                        "provider":   st.session_state.provider,
                    }, auth=True)
                if code == 200:
                    st.session_state.chat_history = [
                        m for m in data.get("history", []) if m["role"] != "system"
                    ]
                    if data.get("diet_plan"):
                        st.session_state.diet_plan = data["diet_plan"]
                        st.toast("✅ تم تحديث جداول الخطة الغذائية فوراً!", icon="🥗")
                    st.rerun()
                else:
                    st.error(data.get("detail", "فشل إرسال الرسالة / Chat failed"))
        elif clear_btn:
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════

def main():
    inject_styles(st.session_state.theme, st.session_state.lang)

    if not st.session_state.token:
        render_auth()
        return

    render_sidebar()

    if st.session_state.page == "form":
        render_form()
    elif st.session_state.page == "chat":
        render_chat()
    else:
        render_form()

if __name__ == "__main__":
    main()
