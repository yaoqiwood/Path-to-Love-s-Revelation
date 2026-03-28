@echo off
echo Activating uv virtual environment...
call .venv\Scripts\activate

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment. Please run 'uv sync' first.
    pause
    exit /b %errorlevel%
)

echo Environment activated successfully.

echo Setting APP_ENV to production...
set APP_ENV=production

echo Starting FastAPI Server in production mode (Uvicorn)...
uvicorn main:app --host 0.0.0.0 --port 8011 --workers 4
