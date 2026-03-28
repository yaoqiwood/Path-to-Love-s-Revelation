@echo off
set "ENVNAME=creative"

echo Activating Conda Environment '%ENVNAME%'...
call conda activate %ENVNAME%

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate conda environment '%ENVNAME%'. Please ensure Conda is in PATH and the environment exists.
    pause
    exit /b %errorlevel%
)

echo Environment activated successfully.

echo Setting APP_ENV to production...
set APP_ENV=production

echo Starting FastAPI Server in production mode (Uvicorn)...
uvicorn main:app --host 0.0.0.0 --port 8011 --workers 4
