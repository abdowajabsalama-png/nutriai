@echo off
title NutriAI - Live Online Permanent Link
chcp 65001 >nul
cls
echo ===============================================================================
echo                🌐 NutriAI - الرابط الدائم للمشروع عبر الإنترنت
echo ===============================================================================
echo.
echo   [1] تأكد أن التطبيق شغال أولاً على جهازك (عبر NutriAI.exe أو launch_nutriai.bat)
echo   [2] جاري فتح الرابط الدائم الرسمي الخاص بك على الإنترنت...
echo.
echo   🔗 الرابط الدائم الثابت لمشروعك (مبيتغيرش أبداً):
echo      👉 https://magnolia-cuddly-debtor.ngrok-free.dev
echo.
echo   📌 تعليمات:
echo      - انسخ الرابط اللي فوق وابعته لزمايلك أو الدكتور في أي وقت.
echo      - يقدروا يفتحوه من أي موبايل، آيفون، أو لابتوب من أي مكان في العالم!
echo      - اترك هذه النافذة مفتوحة طوال فترة التجربة (إغلاقها يوقف الرابط).
echo ===============================================================================
echo.
if exist "%~dp0ngrok.exe" (
    cd /d "%~dp0"
) else (
    cd /d "C:\Users\Abdo\Desktop\pp\nutrial-ai"
)
ngrok.exe http --url=https://magnolia-cuddly-debtor.ngrok-free.dev 8501 --config "C:\Users\Abdo\Desktop\pp\nutrial-ai\ngrok.yml"
pause
