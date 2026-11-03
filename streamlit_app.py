"""
NutriAI - Main Cloud & Standalone Entrypoint for Streamlit Community Cloud
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Execute frontend app directly in global scope
frontend_file = ROOT_DIR / "frontend" / "app.py"
with open(frontend_file, encoding="utf-8") as f:
    code = compile(f.read(), str(frontend_file), "exec")
    exec(code, globals())
