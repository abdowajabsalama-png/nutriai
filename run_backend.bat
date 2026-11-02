@echo off
title NutriAI Backend
cd /d %~dp0
venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
