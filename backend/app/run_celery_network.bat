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

echo Starting Celery Worker in production mode...

@REM celery -A app.core.celery_app worker -l info -P solo -E

celery -A app.core.celery_app worker -n network@%COMPUTERNAME% -Q network_queue -l info -P threads -c 2 -E 