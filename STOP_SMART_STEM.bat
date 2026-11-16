@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>nul
echo Da gui lenh dung SMART STEM (cong 8000).
pause
