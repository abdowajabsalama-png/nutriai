"""
NutriAI - Main Cloud & Standalone Entrypoint for Streamlit Community Cloud
"""
import sys
import os
import threading
import time
import runpy
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Auto-start FastAPI backend if not already active
def ensure_backend_running():
    try:
        import requests
        r = requests.get("http://127.0.0.1:8000/docs", timeout=0.6)
        if r.status_code == 200:
            return
    except Exception:
        pass

    try:
        import uvicorn
        from backend.main import app as fastapi_app
        config = uvicorn.Config(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")
        server = uvicorn.Server(config)
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        import requests
        for _ in range(25):
            time.sleep(0.2)
            try:
                if requests.get("http://127.0.0.1:8000/docs", timeout=0.4).status_code == 200:
                    break
            except Exception:
                pass
    except Exception as e:
        print(f"[NutriAI] Notice: Backend startup: {e}")

ensure_backend_running()

# Execute frontend app
frontend_file = ROOT_DIR / "frontend" / "app.py"
runpy.run_path(str(frontend_file), run_name="__main__")
