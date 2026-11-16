@echo off
cd /d "%~dp0backend"
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
pause
