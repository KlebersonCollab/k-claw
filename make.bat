@echo off
setlocal enabledelayedexpansion

:: Variables
set APP_MODULE=entrypoints.api:app
set HOST=0.0.0.0
set PORT=8000
set PID_FILE=.api.pid
set BOT_PID=.bot.pid

if "%~1"=="" goto help
if "%~1"=="help" goto help
if "%~1"=="setup" goto setup
if "%~1"=="test" goto test
if "%~1"=="test-unit" goto test-unit
if "%~1"=="test-integration" goto test-integration
if "%~1"=="test-e2e" goto test-e2e
if "%~1"=="test-edge" goto test-edge
if "%~1"=="test-cov" goto test-cov
if "%~1"=="test-all" goto test-all
if "%~1"=="install" goto install
if "%~1"=="setup-hooks" goto setup-hooks
if "%~1"=="generate-tools" goto generate-tools
if "%~1"=="run" goto run
if "%~1"=="cli" goto cli
if "%~1"=="bot" goto bot
if "%~1"=="bot-start" goto bot-start
if "%~1"=="bot-stop" goto bot-stop
if "%~1"=="bot-status" goto bot-status
if "%~1"=="yolo" goto yolo
if "%~1"=="clear-memory" goto clear-memory
if "%~1"=="logs" goto logs
if "%~1"=="start" goto start
if "%~1"=="stop" goto stop
if "%~1"=="restart" goto restart
if "%~1"=="status" goto status
if "%~1"=="clean" goto clean
if "%~1"=="webui-backend-install" goto webui-backend-install
if "%~1"=="webui-backend-run" goto webui-backend-run
if "%~1"=="webui-backend-test" goto webui-backend-test
if "%~1"=="webui-frontend-install" goto webui-frontend-install
if "%~1"=="webui-frontend-run" goto webui-frontend-run
if "%~1"=="webui-frontend-build" goto webui-frontend-build
if "%~1"=="webui-frontend-test" goto webui-frontend-test
if "%~1"=="webui-install" goto webui-install
if "%~1"=="webui-run" goto webui-run
if "%~1"=="webui-test" goto webui-test
if "%~1"=="webui-build" goto webui-build

echo Unknown target: %~1
goto help

:help
echo Available commands:
echo   make.bat install      - Install dependencies using uv
echo   make.bat setup        - Initial project setup (copy .env, install deps)
echo   make.bat run          - Run the API in foreground (development)
echo   make.bat start        - Start the API in background
echo   make.bat stop         - Stop the background API process
echo   make.bat restart      - Restart the API
echo   make.bat status       - Check if the API is running
echo   make.bat clean        - Remove temporary files and virtual environment
echo   make.bat cli          - Start the interactive CLI
echo   make.bat bot          - Start the Telegram bot in foreground
echo   make.bat bot-start    - Start the bot in background
echo   make.bat bot-stop     - Stop the background bot process
echo   make.bat bot-status   - Check if the bot is running
echo   make.bat yolo         - Start the CLI in YOLO mode (no approvals)
echo   make.bat clear-memory - Wipe all sessions and long-term memory (DB)
echo   make.bat setup-hooks  - Install pre-commit security hooks
echo   make.bat generate-tools - Consolidate tool manuals into TOOLS.md
echo   make.bat logs         - Show API logs
echo   make.bat test         - Run all tests using pytest
echo   make.bat test-unit    - Run unit tests only
echo   make.bat test-integration - Run integration tests only
echo   make.bat test-e2e     - Run end-to-end tests only
echo   make.bat test-edge    - Run edge case tests only
echo   make.bat test-cov     - Run tests with coverage report (^>= 90%%)
echo   make.bat test-all     - Run all tests with coverage
echo.
echo WebUI commands:
echo   make.bat webui-backend-install  - Install WebUI backend dependencies
echo   make.bat webui-backend-run      - Run WebUI backend (port 8000)
echo   make.bat webui-backend-test     - Run WebUI backend tests
echo   make.bat webui-frontend-install - Install WebUI frontend dependencies
echo   make.bat webui-frontend-run     - Run WebUI frontend (port 5173)
echo   make.bat webui-frontend-build   - Build WebUI frontend for production
echo   make.bat webui-install          - Install all WebUI dependencies
echo   make.bat webui-run              - Run WebUI (backend + frontend)
echo   make.bat webui-test             - Run all WebUI tests
echo   make.bat webui-build            - Build WebUI for production
goto :eof

:setup
if not exist .env (
    echo Copying .env.template to .env...
    copy .env.template .env
)
uv sync
goto :eof

:test
set PYTHONPATH=.
uv run python -m pytest
goto :eof

:test-unit
set PYTHONPATH=.
uv run python -m pytest tests/unit/ -v
goto :eof

:test-integration
set PYTHONPATH=.
uv run python -m pytest tests/integration/ -v
goto :eof

:test-e2e
set PYTHONPATH=.
uv run python -m pytest tests/e2e/ -v
goto :eof

:test-edge
set PYTHONPATH=.
uv run python -m pytest tests/edge_cases/ -v
goto :eof

:test-cov
set PYTHONPATH=.
uv run python -m pytest --cov=. --cov-report=term-missing --cov-fail-under=90
goto :eof

:test-all
set PYTHONPATH=.
uv run python -m pytest --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=90 -v
goto :eof

:install
uv sync
goto :eof

:setup-hooks
uv run pre-commit install
goto :eof

:generate-tools
set PYTHONPATH=.
uv run python -c "from infra.agent_loader import agent_loader; agent_loader.generate_tools_md()"
goto :eof

:run
set PYTHONPATH=.
uv run uvicorn %APP_MODULE% --host %HOST% --port %PORT% --reload
goto :eof

:cli
set PYTHONPATH=.
uv run python entrypoints/cli.py
goto :eof

:bot
set PYTHONPATH=.
uv run python entrypoints/bot.py
goto :eof

:bot-start
if exist %BOT_PID% (
    set /p BOT_PID_VAL=<%BOT_PID%
    echo Bot is already running (PID: !BOT_PID_VAL!)
) else (
    set PYTHONPATH=.
    powershell -Command "$p = Start-Process uv -ArgumentList 'run', 'python', 'entrypoints/bot.py' -NoNewWindow -PassThru -RedirectStandardOutput 'bot.log' -RedirectStandardError 'bot.log'; $p.Id | Out-File -FilePath '%BOT_PID%' -NoNewline -Encoding ascii"
    set /p BOT_PID_VAL=<%BOT_PID%
    echo Bot started in background (PID: !BOT_PID_VAL!)
)
goto :eof

:bot-stop
if exist %BOT_PID% (
    set /p BOT_PID_VAL=<%BOT_PID%
    echo Stopping Bot (PID: !BOT_PID_VAL!)...
    taskkill /PID !BOT_PID_VAL! /T /F >nul 2>&1
    del %BOT_PID%
) else (
    echo Bot is not running.
)
goto :eof

:bot-status
if exist %BOT_PID% (
    set /p BOT_PID_VAL=<%BOT_PID%
    tasklist /FI "PID eq !BOT_PID_VAL!" 2>nul | findstr "!BOT_PID_VAL!" >nul
    if !errorlevel! equ 0 (
        echo Bot is running (PID: !BOT_PID_VAL!)
    ) else (
        echo Bot process PID !BOT_PID_VAL! not found. Cleaning up PID file.
        del %BOT_PID%
    )
) else (
    echo Bot is not running.
)
goto :eof

:yolo
set PYTHONPATH=.
uv run python entrypoints/cli.py --yolo
goto :eof

:clear-memory
echo Wiping all session data and long-term memory...
if exist harness.db del harness.db
if exist harness.db-shm del harness.db-shm
if exist harness.db-wal del harness.db-wal
if exist sessions rmdir /s /q sessions
echo Memory cleared.
goto :eof

:logs
powershell -Command "if (Test-Path api.log) { Get-Content api.log -Wait -Tail 10 } else { Write-Host 'api.log not found' }"
goto :eof

:start
if exist %PID_FILE% (
    set /p PID_VAL=<%PID_FILE%
    echo API is already running (PID: !PID_VAL!)
) else (
    set PYTHONPATH=.
    powershell -Command "$p = Start-Process uv -ArgumentList 'run', 'uvicorn', '%APP_MODULE%', '--host', '%HOST%', '--port', '%PORT%' -NoNewWindow -PassThru -RedirectStandardOutput 'api.log' -RedirectStandardError 'api.log'; $p.Id | Out-File -FilePath '%PID_FILE%' -NoNewline -Encoding ascii"
    set /p PID_VAL=<%PID_FILE%
    echo API started in background (PID: !PID_VAL!)
)
goto :eof

:stop
if exist %PID_FILE% (
    set /p PID_VAL=<%PID_FILE%
    echo Stopping API (PID: !PID_VAL!)...
    taskkill /PID !PID_VAL! /T /F >nul 2>&1
    del %PID_FILE%
) else (
    echo API is not running.
)
goto :eof

:restart
call :stop
call :start
goto :eof

:status
if exist %PID_FILE% (
    set /p PID_VAL=<%PID_FILE%
    tasklist /FI "PID eq !PID_VAL!" 2>nul | findstr "!PID_VAL!" >nul
    if !errorlevel! equ 0 (
        echo API is running (PID: !PID_VAL!)
    ) else (
        echo API process PID !PID_VAL! not found. Cleaning up PID file.
        del %PID_FILE%
    )
) else (
    echo API is not running.
)
goto :eof

:clean
if exist .venv rmdir /s /q .venv
if exist sessions rmdir /s /q sessions
if exist .api.pid del .api.pid
if exist .bot.pid del .bot.pid
if exist api.log del api.log
if exist bot.log del bot.log
powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
goto :eof

:: ==================== WebUI Commands ====================
set WEBUI_BACKEND_DIR=webui\backend
set WEBUI_FRONTEND_DIR=webui\frontend

:webui-backend-install
pushd %WEBUI_BACKEND_DIR%
pip install -r requirements.txt
popd
goto :eof

:webui-backend-run
pushd %WEBUI_BACKEND_DIR%
uvicorn main:app --reload --host 0.0.0.0 --port 8000
popd
goto :eof

:webui-backend-test
pushd %WEBUI_BACKEND_DIR%
python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=90
popd
goto :eof

:webui-frontend-install
pushd %WEBUI_FRONTEND_DIR%
npm install
popd
goto :eof

:webui-frontend-run
pushd %WEBUI_FRONTEND_DIR%
npm run dev
popd
goto :eof

:webui-frontend-build
pushd %WEBUI_FRONTEND_DIR%
npm run build
popd
goto :eof

:webui-frontend-test
pushd %WEBUI_FRONTEND_DIR%
npm run build
popd
goto :eof

:webui-install
call :webui-backend-install
call :webui-frontend-install
goto :eof

:webui-run
echo Starting WebUI...
powershell -Command "Start-Process uvicorn -ArgumentList 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000' -WorkingDirectory '%WEBUI_BACKEND_DIR%' -NoNewWindow"
pushd %WEBUI_FRONTEND_DIR%
npm run dev
popd
goto :eof

:webui-test
call :webui-backend-test
call :webui-frontend-test
goto :eof

:webui-build
call :webui-frontend-build
goto :eof
