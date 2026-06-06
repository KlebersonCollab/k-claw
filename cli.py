import asyncio
import uuid
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markup import escape
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from harness import harness
from persistence import SessionLogger
from dotenv import load_dotenv

load_dotenv()
console = Console()

def display_session_history(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            console.print(f"[bold yellow]You:[/bold yellow] {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.content: console.print(f"[bold magenta]Agent:[/bold magenta] {msg.content}")
        elif isinstance(msg, ToolMessage):
            console.print(f"[dim italic green]Tool Result:[/dim italic green] {msg.content[:100]}...")

async def run_cli():
    console.print(Panel.fit("[bold blue]Agent Harness CLI v2.5[/bold blue]\n[env]AI Provider: [/env]" + os.getenv("AI_PROVIDER", "openai")))

    existing_sessions = SessionLogger.list_sessions()
    session_id = None
    initial_messages = []

    if existing_sessions and Confirm.ask("Resume existing session?"):
        table = Table(title="Past Sessions")
        table.add_column("#", style="cyan"); table.add_column("ID", style="magenta"); table.add_column("Date", style="green")
        for i, s in enumerate(existing_sessions[:5], 1): table.add_row(str(i), s["id"], s["created_at"])
        console.print(table)
        choice = Prompt.ask("Select number", default="1")
        if choice.isdigit() and 1 <= int(choice) <= len(existing_sessions):
            session_id = existing_sessions[int(choice)-1]["id"]
            logger = SessionLogger(session_id)
            initial_messages = logger.get_message_history()
            display_session_history(initial_messages)

    if not session_id: session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    is_new_session = (len(initial_messages) == 0)

    harness_metadata = {
        "context_budget": 10, "iteration_count": 0, "session_id": session_id,
        "permissions": os.getenv("HARNESS_PERMISSIONS", "execute"),
        "context_summary": "", "incognito": False
    }

    console.print(f"[bold green]Session ID:[/bold green] {session_id}")

    while True:
        user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
        if user_input.lower() in ["exit", "quit"]: break

        if is_new_session:
            current_input = {**harness_metadata, "messages": [HumanMessage(content=user_input)]}
            is_new_session = False
        else:
            current_input = {"messages": [HumanMessage(content=user_input)], **harness_metadata}

        try:
            # We don't use global status here anymore. Nodes manage their own.
            current_state = await harness.ainvoke(current_input, config=config)

            # Final AI response display
            # (Sub-agents and Tool results were already printed by nodes in logic.py)
            last_msg = current_state["messages"][-1]
            if isinstance(last_msg, AIMessage) and last_msg.content:
                console.print(f"\n[bold magenta]Agent:[/bold magenta]\n{last_msg.content}\n")
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

        console.print("[dim]─[/dim]" * 20)

if __name__ == "__main__":
    try: asyncio.run(run_cli())
    except KeyboardInterrupt: console.print("\n[yellow]Session ended.[/yellow]")
