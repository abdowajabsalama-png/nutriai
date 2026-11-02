@echo off
title NutriAI
cd /d "%~dp0"

:: Kill any stale processes on 8000 and 8501 to guarantee fresh code reload
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8501') do taskkill /f /pid %%a >nul 2>&1

:: Start hidden backend and frontend
wscript.exe start_hidden.vbs

:: Wait for servers to spin up
timeout /t 3 /nobreak >nul

:: Open API tab first
start http://127.0.0.1:8000/docs

:: Wait a brief moment and open Website tab so it is active in front
timeout /t 1 /nobreak >nul
start http://localhost:8501

exit
