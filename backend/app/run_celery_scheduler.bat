@echo off
set "ENVNAME=creative"

echo Activating Conda Environment '%ENVNAME%'...
call conda activate %ENVNAME%

if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate conda environment '%ENVNAME%'.
    pause
    exit /b %errorlevel%
)

echo Environment activated successfully.

echo Setting APP_ENV to production...
set APP_ENV=production

echo Starting Celery Beat Scheduler in production mode...

celery -A app.core.celery_app beat -l info