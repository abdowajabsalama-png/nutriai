@echo off
title NutriAI Runner
echo ====================================================
echo Starting NutriAI Backend and Frontend...
echo ====================================================

start "NutriAI Backend" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
start "NutriAI Frontend" cmd /k "cd /d %~dp0 && venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501"

echo.
echo NutriAI is running!
echo Backend:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)
echo Frontend: http://localhost:8501
echo.
pause
