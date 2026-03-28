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

echo Starting Celery Beat Scheduler in production mode...

celery -A app.core.celery_app beat -l info