@echo off
title NutriAI - Live Online Sharing
chcp 65001 >nul
cls
echo ===============================================================================
echo                🌐 NutriAI - مشاركة الموقع عبر الإنترنت للزملاء
echo ===============================================================================
echo.
echo   [1] تأكد أن التطبيق شغال أولاً على جهازك (عبر NutriAI.exe أو launch_nutriai.bat)
echo   [2] جاري الاتصال وتوليد رابط إنترنت عام مشفر ومباشر (HTTPS)...
echo.
echo   📌 تعليمات الاستخدام:
echo      - سيظهر لك بالأسفل رابط ينتهي بـ .lhr.life (يبدأ بـ https://)
echo      - انسخ الرابط وابعته لأي زميل على واتساب أو ماسنجر.
echo      - يقدر يفتحه من أي موبايل، آيفون، أو لابتوب من أي مكان في العالم!
echo      - اترك هذه النافذة مفتوحة طوال فترة التجربة (إغلاقها يوقف الرابط).
echo.
echo ===============================================================================
echo.
ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -R 80:localhost:8501 nokey@localhost.run
if errorlevel 1 (
    echo.
    echo [!] جاري المحاولة عبر خادم بديل (pinggy)...
    echo.
    ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8501 a.pinggy.io
)
echo.
echo تم إنهاء الاتصال.
pause
