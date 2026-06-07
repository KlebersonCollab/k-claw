# Makefile for Agent Harness

# Variables
APP_MODULE = entrypoints.api:app
HOST = 0.0.0.0
PORT = 8000
PID_FILE = .api.pid
BOT_PID = .bot.pid

.PHONY: install run start stop restart clean status help cli bot bot-start bot-stop bot-status clear-memory logs setup-hooks generate-tools yolo setup test

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
	@echo "  make test         - Run tests using pytest"

setup:
	@if [ ! -f .env ]; then \
		echo "Copying .env.template to .env..."; \
		cp .env.template .env; \
	fi
	uv sync

test:
	PYTHONPATH=. uv run pytest

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
