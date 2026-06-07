"""
Agent Harness — Telegram Bot Entrypoint
========================================
Interage com o harness via Telegram. Cada chat_id possui sua própria sessão.
Uso:
    python entrypoints/bot.py
Requer TELEGRAM_BOT_TOKEN no .env
"""

import asyncio
import json
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from core.harness import harness
from core.ui_interface import EventType, UIInterface, set_ui
from infra.persistence import SessionLogger

load_dotenv()

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Session persistence (chat_id → session_id)
# ──────────────────────────────────────────────
SESSIONS_FILE = Path("telegram_sessions.json")

def load_chat_sessions() -> Dict[str, str]:
    if SESSIONS_FILE.exists():
        try:
            return json.loads(SESSIONS_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_chat_sessions(data: Dict[str, str]):
    SESSIONS_FILE.write_text(json.dumps(data, indent=2))

chat_sessions: Dict[str, str] = load_chat_sessions()

# ──────────────────────────────────────────────
# YOLO mode store (chat_id → bool)
# ──────────────────────────────────────────────
yolo_modes: Dict[str, bool] = {}

# ──────────────────────────────────────────────
# Pending approvals (approval_id → Future)
# ──────────────────────────────────────────────
pending_approvals: Dict[str, asyncio.Future] = {}

# ──────────────────────────────────────────────
# Telegram UI Interface
# ──────────────────────────────────────────────
MAX_TELEGRAM_MSG = 4096  # hard limit do Telegram


def truncate(text: str, limit: int = MAX_TELEGRAM_MSG) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20] + "\n…(truncated)"


class TelegramInterface(UIInterface):
    """Envia eventos do harness para o chat do Telegram."""

    def __init__(self, bot, chat_id: int):
        self.bot = bot
        self.chat_id = chat_id

    async def on_event(self, event_type: EventType, data: dict):
        try:
            if event_type == EventType.THINKING_START:
                agent = data.get("agent", "Agent")
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🧠 *{agent} is thinking…*",
                    parse_mode="Markdown",
                )
            elif event_type == EventType.THINKING_END:
                pass  # silenciar fim do pensamento
            elif event_type == EventType.TOOL_START:
                tool = data.get("tool", "unknown")
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"🔧 Executing `{tool}`…",
                    parse_mode="Markdown",
                )
            elif event_type == EventType.TOOL_END:
                pass
            elif event_type == EventType.COMPACTION_START:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text="📦 Compacting context…",
                )
            elif event_type == EventType.ERROR:
                msg = data.get("message", "Unknown error")
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"❌ *Error:* {msg}",
                    parse_mode="Markdown",
                )
            elif event_type == EventType.APPROVAL_REQUIRED:
                approval_id = data.get("approval_id", "")
                tool = data.get("tool", "unknown")
                args = data.get("args", {})
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "✅ Approve",
                                callback_data=f"approve:{approval_id}",
                            ),
                            InlineKeyboardButton(
                                "❌ Deny",
                                callback_data=f"deny:{approval_id}",
                            ),
                        ]
                    ]
                )
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=(
                        f"⚠️ *Approval Required*\n"
                        f"Tool: `{tool}`\n"
                        f"Args: `{truncate(str(args), 500)}`"
                    ),
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
        except Exception as exc:
            logger.error("TelegramInterface.on_event error: %s", exc)

    async def request_approval(self, tool_name: str, args: dict) -> bool:
        approval_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        pending_approvals[approval_id] = future

        # Envia mensagem com botões (via on_event pattern)
        await self.on_event(
            EventType.APPROVAL_REQUIRED,
            {"approval_id": approval_id, "tool": tool_name, "args": args},
        )

        try:
            result = await future
            return result
        finally:
            pending_approvals.pop(approval_id, None)


# ──────────────────────────────────────────────
# Bot command handlers
# ──────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session_id = chat_sessions.get(chat_id)
    yolo = yolo_modes.get(chat_id, False)

    if session_id:
        logger = SessionLogger(session_id)
        history = logger.get_message_history()
        msg = (
            f"🤖 *Agent Harness Bot*\n\n"
            f"Session: `{session_id[:8]}…`\n"
            f"Messages in history: {len(history)}\n"
            f"YOLO mode: {'🔴 ON' if yolo else '🟢 OFF'}\n\n"
            f"Send me a message to interact!\n"
            f"Commands: /new /yolo /status"
        )
    else:
        msg = (
            "🤖 *Agent Harness Bot*\n\n"
            "No active session yet. Send any message to start, or use /new.\n\n"
            "Commands: /new /yolo /status"
        )
    await safe_reply(update, msg, parse_mode="Markdown")


async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session_id = str(uuid.uuid4())
    chat_sessions[chat_id] = session_id
    save_chat_sessions(chat_sessions)
    yolo_modes[chat_id] = False
    await safe_reply(
        update,
        f"🆕 New session started!\nSession ID: `{session_id}`",
        parse_mode="Markdown",
    )


async def cmd_yolo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    current = yolo_modes.get(chat_id, False)
    yolo_modes[chat_id] = not current
    new_state = yolo_modes[chat_id]
    emoji = "🔴" if new_state else "🟢"
    await safe_reply(
        update,
        f"{emoji} YOLO mode: *{'ON' if new_state else 'OFF'}*",
        parse_mode="Markdown",
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    session_id = chat_sessions.get(chat_id)
    yolo = yolo_modes.get(chat_id, False)

    if not session_id:
        await update.message.reply_text("No active session. Send a message or /new.")
        return

    slog = SessionLogger(session_id)
    history = slog.get_message_history()
    await safe_reply(
        update,
        (
            f"📊 *Session Status*\n\n"
            f"Session ID: `{session_id}`\n"
            f"Messages: {len(history)}\n"
            f"YOLO: {'🔴 ON' if yolo else '🟢 OFF'}"
        ),
        parse_mode="Markdown",
    )


async def safe_reply(update: Update, text: str, parse_mode: str = "Markdown", **kwargs):
    """Tenta enviar mensagem com formatação, fallback para texto simples se falhar."""
    try:
        if update.message:
            return await update.message.reply_text(text, parse_mode=parse_mode, **kwargs)
        elif update.callback_query and update.callback_query.message:
            return await update.callback_query.message.reply_text(
                text, parse_mode=parse_mode, **kwargs
            )
    except BadRequest as e:
        if "Can't parse entities" in str(e):
            # Fallback para texto simples se o Markdown estiver quebrado
            if update.message:
                return await update.message.reply_text(text, parse_mode=None, **kwargs)
            elif update.callback_query and update.callback_query.message:
                return await update.callback_query.message.reply_text(
                    text, parse_mode=None, **kwargs
                )
        raise e


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text or ""

    # Ignorar comandos que porventura caiam aqui
    if text.startswith("/"):
        return

    # Limite de tamanho
    if len(text) > 10000:
        await update.message.reply_text(
            "❌ Message too long (max 10 000 characters)."
        )
        return

    # Criar sessão se não existir
    if chat_id not in chat_sessions:
        session_id = str(uuid.uuid4())
        chat_sessions[chat_id] = session_id
        save_chat_sessions(chat_sessions)
        yolo_modes[chat_id] = False
        logger.info("Auto-created session %s for chat %s", session_id, chat_id)

    session_id = chat_sessions[chat_id]
    yolo = yolo_modes.get(chat_id, False)

    # Configurar UI para este chat
    tg_ui = TelegramInterface(bot=context.bot, chat_id=int(chat_id))
    set_ui(tg_ui)

    config = {"configurable": {"thread_id": session_id}}

    harness_metadata = {
        "context_budget": 50,
        "max_iterations": 50,
        "iteration_count": 0,
        "session_id": session_id,
        "permissions": os.getenv("HARNESS_PERMISSIONS", "execute"),
        "context_summary": "",
        "incognito": False,
        "yolo": yolo,
    }

    input_data = {"messages": [HumanMessage(content=text)], **harness_metadata}

    try:
        final_state = await harness.ainvoke(input_data, config=config)
        last_msg = final_state["messages"][-1]
        response_text = last_msg.content or "(no response)"

        # Telegram tem limite de 4096 chars por mensagem
        if len(response_text) <= MAX_TELEGRAM_MSG:
            await safe_reply(update, response_text, parse_mode="Markdown")
        else:
            # Enviar em partes
            for i in range(0, len(response_text), MAX_TELEGRAM_MSG):
                chunk = response_text[i : i + MAX_TELEGRAM_MSG]
                await safe_reply(update, chunk, parse_mode="Markdown")

    except Exception as exc:
        logger.exception("Harness error for chat %s", chat_id)
        await safe_reply(
            update, f"❌ *Error:* {truncate(str(exc), 500)}", parse_mode="Markdown"
        )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resolve aprovações pendentes via botões inline."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if ":" not in data:
        return

    action, approval_id = data.split(":", 1)

    if approval_id in pending_approvals:
        future = pending_approvals[approval_id]
        if not future.done():
            approved = action == "approve"
            future.set_result(approved)
            text = "✅ Approved" if approved else "❌ Denied"
            await query.edit_message_text(text=f"{query.message.text}\n\n*{text}*", parse_mode="Markdown")
        else:
            await query.edit_message_text(
                text=f"{query.message.text}\n\n⚠️ Already resolved",
                parse_mode="Markdown",
            )
    else:
        await query.edit_message_text(
            text=f"{query.message.text}\n\n⚠️ Expired or unknown approval",
            parse_mode="Markdown",
        )


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN not set! Add it to your .env file."
        )
        raise SystemExit(1)

    app = Application.builder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("new", cmd_new))
    app.add_handler(CommandHandler("yolo", cmd_yolo))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    logger.info("🤖 Telegram Bot starting…")
    app.run_polling()


if __name__ == "__main__":
    main()
