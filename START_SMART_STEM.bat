@echo off
chcp 65001 >nul
setlocal EnableExtensions
 title SMART STEM 2.0 - ALL IN ONE
cd /d "%~dp0"
color 0A
echo =====================================================
echo   SMART COMPUTER ^& NETWORK STEM 2.0 - ALL IN ONE
echo =====================================================
echo.

REM Use the Python version already selected/installed on this computer.
set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 set "PY_CMD=py"
if not defined PY_CMD (
  where python >nul 2>nul
  if not errorlevel 1 set "PY_CMD=python"
)
if not defined PY_CMD (
  echo [LOI] Khong tim thay Python trong may.
  echo Hay cai Python va chon Add Python to PATH, sau do chay lai.
  pause
  exit /b 1
)

for /f "delims=" %%V in ('%PY_CMD% -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))" 2^>nul') do set "BASE_PY=%%V"
if not defined BASE_PY (
  echo [LOI] Khong doc duoc phien ban Python hien tai.
  %PY_CMD% --version
  pause
  exit /b 1
)
echo Python dang duoc chon: %BASE_PY%
%PY_CMD% --version

REM Recreate virtual environment only if it was built with another Python minor version.
set "VENV_PY="
if exist ".venv\Scripts\python.exe" for /f "delims=" %%V in ('.venv\Scripts\python.exe -c "import sys; print(str(sys.version_info.major)+'.'+str(sys.version_info.minor))" 2^>nul') do set "VENV_PY=%%V"
if not exist ".venv\Scripts\python.exe" goto make_venv
if not "%VENV_PY%"=="%BASE_PY%" (
  echo Moi truong cu dung Python %VENV_PY%, se tao lai bang Python %BASE_PY%...
  rmdir /s /q .venv
  goto make_venv
)
goto install_deps

:make_venv
echo.
echo [1/3] Tao moi truong rieng bang Python dang co...
%PY_CMD% -m venv .venv
if errorlevel 1 goto fail

:install_deps
echo.
echo [2/3] Cai dat cac thu vien tuong thich voi Python %BASE_PY%...
.venv\Scripts\python.exe -m ensurepip --upgrade
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 goto fail
.venv\Scripts\python.exe -m pip install --disable-pip-version-check --upgrade -r backend\requirements.txt
if errorlevel 1 goto fail

echo.
echo [3/3] Kiem tra va khoi dong he thong...
.venv\Scripts\python.exe -c "import fastapi, uvicorn, sqlalchemy, qrcode; print('Kiem tra thu vien: OK')"
if errorlevel 1 goto fail
start "SMART STEM - Trinh duyet" cmd /c "timeout /t 3 >nul & start http://127.0.0.1:8000"
echo.
echo He thong dang chay. De dung, nhan Ctrl+C trong cua so nay.
echo Truy cap: http://127.0.0.1:8000
echo Dien thoai cung mang: http://IP-MAY-TINH:8000
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000
if errorlevel 1 goto fail
pause
exit /b 0

:fail
echo.
echo =====================================================
echo KHOI DONG THAT BAI.
echo Python dang dung: %BASE_PY%
echo Hay chup anh toan bo cua so loi va gui lai de toi sua dung loi.
echo Neu loi tai thu vien, kiem tra ket noi Internet.
echo =====================================================
pause
exit /b 1
