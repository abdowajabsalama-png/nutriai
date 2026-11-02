@echo off
title NutriAI - Live Online Sharing
chcp 65001 >nul
cls
echo ===============================================================================
echo                🌐 NutriAI - مشاركة الموقع عبر الإنترنت للزملاء
echo ===============================================================================
echo.
echo   [1] تأكد أن التطبيق شغال أولاً على جهازك (عبر NutriAI.exe أو launch_nutriai.bat)
echo   [2] جاري الاتصال بخادم النفق وتوليد رابط إنترنت عام مشفر (HTTPS)...
echo.
echo   📌 تعليمات الاستخدام:
echo      - سيظهر لك رابط خاص يبدأ بـ https://xxxxxx.a.pinggy.link
echo      - انسخ الرابط وابعته لأي زميل في الفريق على واتساب أو ماسنجر.
echo      - يقدر يفتحه من أي موبايل، آيفون، أو لابتوب من أي مكان في العالم!
echo      - اترك هذه النافذة مفتوحة طوال فترة التجربة (إغلاقها يوقف الرابط).
echo.
echo ===============================================================================
echo.
ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:8501 a.pinggy.io
if errorlevel 1 (
    echo.
    echo [!] جاري المحاولة عبر خادم بديل (localhost.run)...
    echo.
    ssh -o StrictHostKeyChecking=no -R 80:localhost:8501 nokey@localhost.run
)
echo.
echo تم إنهاء الاتصال.
pause
