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

echo Starting Celery Worker in production mode...

celery -A app.core.celery_app worker -n network@%COMPUTERNAME% -Q network_queue -l info -P threads -c 2 -E