import asyncio
import uuid
import sys
import os
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markup import escape
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from harness import harness
from persistence import SessionLogger
from dotenv import load_dotenv
from ui_interface import UIInterface, EventType, set_ui

load_dotenv()
console = Console()

class CLIInterface(UIInterface):
    def __init__(self):
        self.status = None

    async def on_event(self, event_type: EventType, data: dict):
        if event_type == EventType.THINKING_START:
            self.status = console.status(f"[bold cyan]{data.get('agent', 'Agent')} is thinking...[/bold cyan]")
            self.status.start()
        elif event_type == EventType.THINKING_END:
            if self.status:
                self.status.stop()
                self.status = None
        elif event_type == EventType.TOOL_START:
            console.print(f"[dim green]Executing {data.get('tool')}...[/dim green]")
        elif event_type == EventType.TOOL_END:
            pass # We show results via message history
        elif event_type == EventType.COMPACTION_START:
            console.print("[bold yellow]Compacting context...[/bold yellow]")
        elif event_type == EventType.ERROR:
            console.print(f"[bold red]Error:[/bold red] {data.get('message')}")

    async def request_approval(self, tool_name: str, args: dict) -> bool:
        if self.status: self.status.stop()
        console.print("\n")
        console.print(Panel(f"[bold red]⚠️ Verification Needed[/bold red]\n[yellow]Tool:[/yellow] {tool_name}\n[yellow]Args:[/yellow] {escape(str(args))}",
                            title="Action Pending", border_style="red"))
        approved = await asyncio.to_thread(Confirm.ask, f"Allow {tool_name}?")
        if self.status: self.status.start()
        return approved

def display_session_history(messages):
    for msg in messages:
        if isinstance(msg, HumanMessage):
            console.print(f"[bold yellow]You:[/bold yellow] {msg.content}")
        elif isinstance(msg, AIMessage):
            if msg.content: console.print(f"\n[bold magenta]Agent:[/bold magenta]\n{msg.content}\n")
        elif isinstance(msg, ToolMessage):
            console.print(f"[dim italic green]Tool Result:[/dim italic green] {escape(str(msg.content[:100]))}...")

async def run_cli():
    parser = argparse.ArgumentParser(description="Agent Harness CLI")
    parser.add_argument("--yolo", action="store_true", help="Bypass all security approvals")
    args = parser.parse_args()

    # Set the global UI to this CLI implementation
    cli = CLIInterface()
    set_ui(cli)

    yolo_status = " [bold red](YOLO MODE)[/bold red]" if args.yolo else ""
    console.print(Panel.fit(f"[bold blue]Agent Harness CLI v2.6[/bold blue]{yolo_status}\n[env]AI Provider: [/env]" + os.getenv("AI_PROVIDER", "openai")))

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
        "context_budget": 50, "max_iterations": 25, "iteration_count": 0,
        "session_id": session_id,
        "permissions": os.getenv("HARNESS_PERMISSIONS", "execute"),
        "context_summary": "", "incognito": False, "yolo": args.yolo
    }

    console.print(f"[bold green]Session ID:[/bold green] {session_id}")

    while True:
        user_input = Prompt.ask("[bold yellow]You[/bold yellow]")
        if user_input.lower() in ["exit", "quit"]: break

        if len(user_input) > 10000:
            console.print("[bold red]Error:[/bold red] Message too long (max 10000 characters).")
            continue

        if is_new_session:
            current_input = {**harness_metadata, "messages": [HumanMessage(content=user_input)]}
            is_new_session = False
        else:
            current_input = {"messages": [HumanMessage(content=user_input)], **harness_metadata}

        try:
            prev_history_len = len(initial_messages) if 'current_state' not in locals() else len(current_state["messages"])

            # Use streaming to catch intermediate events if we want, or just rely on the UI Event callbacks
            # Since we implemented the EventBus (ui_interface), intermediate steps are already logged
            # via console.print inside on_event (e.g., "Executing tool_name...").
            # The final ainvoke result will just contain the cleaned-up "messages".

            current_state = await harness.ainvoke(current_input, config=config)

            # Display ONLY final AI responses from the main message history
            new_msgs = current_state.get("messages", [])[prev_history_len:]
            for msg in new_msgs:
                if isinstance(msg, AIMessage) and msg.content:
                    console.print(f"\n[bold magenta]Agent:[/bold magenta]\n{msg.content}\n")

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

        console.print("[dim]─[/dim]" * 20)

if __name__ == "__main__":
    try: asyncio.run(run_cli())
    except KeyboardInterrupt: console.print("\n[yellow]Session ended.[/yellow]")
