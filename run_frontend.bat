@echo off
title NutriAI Frontend
cd /d %~dp0
venv\Scripts\python.exe -m streamlit run frontend/app.py --server.port 8501
pause
