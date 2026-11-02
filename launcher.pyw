import os
import sys
import socket
import subprocess
import time
import webbrowser

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launcher.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

def is_port_open(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

def kill_ports(ports=(8000, 8501)):
    for port in ports:
        try:
            cmd = f'netstat -ano | findstr /R /C:":{port} .*LISTENING"'
            out = subprocess.check_output(cmd, shell=True).decode()
            for line in out.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pid = parts[-1]
                    if int(pid) != os.getpid():
                        subprocess.call(f'taskkill /F /PID {pid} >nul 2>&1', shell=True)
        except Exception:
            pass

try:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(PROJECT_DIR)
    log("Launcher started - killing stale processes for clean reload")

    # Clean stale instances to ensure updated code runs
    kill_ports((8000, 8501))
    time.sleep(0.5)

    VENV_PYTHON = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")
    CREATE_NO_WINDOW = 0x08000000

    log("Starting Backend server (FastAPI)...")
    subprocess.Popen(
        [VENV_PYTHON, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=PROJECT_DIR,
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    log("Starting Frontend server (Streamlit)...")
    subprocess.Popen(
        [VENV_PYTHON, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.headless", "true"],
        cwd=PROJECT_DIR,
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for ports to become active
    for i in range(50):
        if is_port_open(8000) and is_port_open(8501):
            log(f"Services ready in {(i+1)*100}ms")
            break
        time.sleep(0.1)

    time.sleep(1)

    # Open API tab first, then Website tab so Website is active in front!
    log("Opening browser tabs...")
    try:
        os.startfile("http://127.0.0.1:8000/docs")
    except Exception:
        webbrowser.open("http://127.0.0.1:8000/docs")

    time.sleep(0.8)

    try:
        os.startfile("http://localhost:8501")
    except Exception:
        webbrowser.open("http://localhost:8501")

    log("Both pages opened successfully. Supervisor active.")

    while True:
        time.sleep(60)

except Exception as ex:
    log(f"FATAL ERROR in launcher: {ex}")
    import traceback
    log(traceback.format_exc())
