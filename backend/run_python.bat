@echo off
echo Activating uv virtual environment...
call .venv\Scripts\activate

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment. Please run 'uv sync' first.
    pause
    exit /b %errorlevel%
)

echo Environment activated successfully.

if "%~1"=="" (
    set APP_ENV=development
) else (
    set APP_ENV=%~1
)

echo Starting FastAPI Server with APP_ENV=%APP_ENV% ...
python -m uvicorn main:app --host 0.0.0.0 --port 8011 --workers 1
