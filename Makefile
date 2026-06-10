# Makefile for Agent Harness

# Variables
APP_MODULE = entrypoints.api:app
HOST = 0.0.0.0
PORT = 8000
PID_FILE = .api.pid
BOT_PID = .bot.pid

.PHONY: install run start stop restart clean status help cli bot bot-start bot-stop bot-status clear-memory logs setup-hooks generate-tools yolo setup test test-unit test-integration test-e2e test-edge test-cov test-all webui-backend-install webui-backend-run webui-backend-test webui-frontend-install webui-frontend-run webui-frontend-build webui-frontend-test webui-install webui-run webui-test webui-build

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make setup        - Initial project setup (copy .env, install deps)"
	@echo "  make run          - Run the API in foreground (development)"
	@echo "  make start        - Start the API in background"
	@echo "  make stop         - Stop the background API process"
	@echo "  make restart      - Restart the API"
	@echo "  make status       - Check if the API is running"
	@echo "  make clean        - Remove temporary files and virtual environment"
	@echo "  make cli          - Start the interactive CLI"
	@echo "  make bot          - Start the Telegram bot in foreground"
	@echo "  make bot-start    - Start the bot in background"
	@echo "  make bot-stop     - Stop the background bot process"
	@echo "  make bot-status   - Check if the bot is running"
	@echo "  make yolo         - Start the CLI in YOLO mode (no approvals)"
	@echo "  make clear-memory - Wipe all sessions and long-term memory (DB)"
	@echo "  make setup-hooks  - Install pre-commit security hooks"
	@echo "  make generate-tools - Consolidate tool manuals into TOOLS.md"
	@echo "  make logs         - Show API logs"
	@echo "  make test         - Run all tests using pytest"
	@echo "  make test-unit    - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-e2e     - Run end-to-end tests only"
	@echo "  make test-edge    - Run edge case tests only"
	@echo "  make test-cov     - Run tests with coverage report (>= 90%)"
	@echo "  make test-all     - Run all tests with coverage"
	@echo ""
	@echo "WebUI commands:"
	@echo "  make webui-backend-install  - Install WebUI backend dependencies"
	@echo "  make webui-backend-run      - Run WebUI backend (port 8000)"
	@echo "  make webui-backend-test     - Run WebUI backend tests"
	@echo "  make webui-frontend-install - Install WebUI frontend dependencies"
	@echo "  make webui-frontend-run     - Run WebUI frontend (port 5173)"
	@echo "  make webui-frontend-build   - Build WebUI frontend for production"
	@echo "  make webui-install          - Install all WebUI dependencies"
	@echo "  make webui-run              - Run WebUI (backend + frontend)"
	@echo "  make webui-test             - Run all WebUI tests"
	@echo "  make webui-build            - Build WebUI for production"

setup:
	@if [ ! -f .env ]; then \
		echo "Copying .env.template to .env..."; \
		cp .env.template .env; \
	fi
	uv sync

test:
	PYTHONPATH=. uv run python -m pytest

test-unit:
	PYTHONPATH=. uv run python -m pytest tests/unit/ -v

test-integration:
	PYTHONPATH=. uv run python -m pytest tests/integration/ -v

test-e2e:
	PYTHONPATH=. uv run python -m pytest tests/e2e/ -v

test-edge:
	PYTHONPATH=. uv run python -m pytest tests/edge_cases/ -v

test-cov:
	PYTHONPATH=. uv run python -m pytest --cov=. --cov-report=term-missing --cov-fail-under=90

test-all:
	PYTHONPATH=. uv run python -m pytest --cov=. --cov-report=term-missing --cov-report=html --cov-fail-under=90 -v

install:
	uv sync

setup-hooks:
	uv run pre-commit install

generate-tools:
	PYTHONPATH=. uv run python -c "from infra.agent_loader import agent_loader; agent_loader.generate_tools_md()"

run:
	PYTHONPATH=. uv run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

cli:
	PYTHONPATH=. uv run python entrypoints/cli.py

bot:
	PYTHONPATH=. uv run python entrypoints/bot.py

bot-start:
	@if [ -f $(BOT_PID) ]; then \
		echo "Bot is already running (PID: $$(cat $(BOT_PID)))"; \
	else \
		PYTHONPATH=. uv run python entrypoints/bot.py > bot.log 2>&1 & echo $$! > $(BOT_PID); \
		echo "Bot started in background (PID: $$(cat $(BOT_PID)))"; \
	fi

bot-stop:
	@if [ -f $(BOT_PID) ]; then \
		PID=$$(cat $(BOT_PID)); \
		echo "Stopping Bot (PID: $$PID)..."; \
		kill $$PID && rm $(BOT_PID) || (echo "Process not found. Cleaning up PID file." && rm $(BOT_PID)); \
	else \
		echo "Bot is not running."; \
	fi

bot-status:
	@if [ -f $(BOT_PID) ]; then \
		echo "Bot is running (PID: $$(cat $(BOT_PID)))"; \
		ps -p $$(cat $(BOT_PID)); \
	else \
		echo "Bot is not running."; \
	fi

yolo:
	PYTHONPATH=. uv run python entrypoints/cli.py --yolo

clear-memory:
	@echo "Wiping all session data and long-term memory..."
	rm -f harness.db harness.db-shm harness.db-wal
	rm -rf sessions
	@echo "Memory cleared."

logs:
	tail -f api.log

start:
	@if [ -f $(PID_FILE) ]; then \
		echo "API is already running (PID: $$(cat $(PID_FILE)))"; \
	else \
		PYTHONPATH=. uv run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) > api.log 2>&1 & echo $$! > $(PID_FILE); \
		echo "API started in background (PID: $$(cat $(PID_FILE)))"; \
	fi

stop:
	@if [ -f $(PID_FILE) ]; then \
		PID=$$(cat $(PID_FILE)); \
		echo "Stopping API (PID: $$PID)..."; \
		kill $$PID && rm $(PID_FILE) || (echo "Process not found. Cleaning up PID file." && rm $(PID_FILE)); \
	else \
		echo "API is not running."; \
	fi

restart: stop start

status:
	@if [ -f $(PID_FILE) ]; then \
		echo "API is running (PID: $$(cat $(PID_FILE)))"; \
		ps -p $$(cat $(PID_FILE)); \
	else \
		echo "API is not running."; \
	fi

clean:
	rm -rf .venv
	rm -rf sessions
	rm -f .api.pid .bot.pid
	rm -f api.log bot.log
	find . -type d -name "__pycache__" -exec rm -rf {} +

# ==================== WebUI Commands ====================

WEBUI_BACKEND_DIR = webui/backend
WEBUI_FRONTEND_DIR = webui/frontend

## WebUI Backend
webui-backend-install:
	cd $(WEBUI_BACKEND_DIR) && pip install -r requirements.txt

webui-backend-run:
	cd $(WEBUI_BACKEND_DIR) && uvicorn main:app --reload --host 0.0.0.0 --port 8000

webui-backend-test:
	cd $(WEBUI_BACKEND_DIR) && python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=90

## WebUI Frontend
webui-frontend-install:
	cd $(WEBUI_FRONTEND_DIR) && npm install

webui-frontend-run:
	cd $(WEBUI_FRONTEND_DIR) && npm run dev

webui-frontend-build:
	cd $(WEBUI_FRONTEND_DIR) && npm run build

webui-frontend-test:
	cd $(WEBUI_FRONTEND_DIR) && npm run build

## WebUI Combined
webui-install: webui-backend-install webui-frontend-install

webui-run:
	@echo "Starting WebUI..."
	@cd $(WEBUI_BACKEND_DIR) && uvicorn main:app --reload --host 0.0.0.0 --port 8000 & \
	cd $(WEBUI_FRONTEND_DIR) && npm run dev

webui-test: webui-backend-test webui-frontend-test

webui-build: webui-frontend-build
