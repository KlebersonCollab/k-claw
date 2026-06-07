"""
Life Cycle Hooks — Pre-tool e Post-tool extensibility for the Agent Harness.

Pre-tool hooks:  fire BEFORE a tool executes. Can allow, deny, or modify the call.
Post-tool hooks: fire AFTER a tool executes. Used for audit, logging, observability.

Protocol inspired by "What is an Agent Harness" study:
  "Hooks let you inject custom logic before or after a tool runs
   without touching the harness itself."
"""

from typing import Any, Dict, Callable, List
from dataclasses import dataclass, field


@dataclass
class HookResult:
    """Result returned by a pre-tool hook.

    Attributes:
        allowed: If False, the tool call is denied and does not execute.
        modified_args: If non-empty, replaces the original tool arguments.
    """
    allowed: bool = True
    modified_args: Dict[str, Any] = field(default_factory=dict)


class HookManager:
    """Manages pre-tool and post-tool hooks for the harness.

    Usage:
        # Register a pre-tool hook that blocks `run_shell` with `sudo`
        async def block_sudo(tool_name, tool_args, context):
            if tool_name == "run_shell" and "sudo" in tool_args.get("command", ""):
                return HookResult(allowed=False)
            return HookResult(allowed=True)

        hook_manager.register_pre_tool(block_sudo)

        # Register a post-tool hook that logs tool usage
        async def log_usage(tool_name, tool_args, result, context):
            print(f"[AUDIT] {tool_name} called in session {context.get('session_id')}")

        hook_manager.register_post_tool(log_usage)
    """

    def __init__(self):
        self.pre_tool_hooks: List[Callable] = []
        self.post_tool_hooks: List[Callable] = []

    def register_pre_tool(self, hook: Callable) -> None:
        """Register a pre-tool hook.

        Hook signature:
            async (tool_name: str, tool_args: dict, context: dict) -> HookResult

        - Return HookResult(allowed=False) to deny the call.
        - Return HookResult(modified_args={...}) to modify arguments.
        - Return HookResult() (default) to allow without modification.
        """
        self.pre_tool_hooks.append(hook)

    def register_post_tool(self, hook: Callable) -> None:
        """Register a post-tool hook.

        Hook signature:
            async (tool_name: str, tool_args: dict, result: str, context: dict) -> None

        Post-tool hooks are for audit/observability only — they cannot block.
        """
        self.post_tool_hooks.append(hook)

    def clear_all(self) -> None:
        """Remove all registered hooks."""
        self.pre_tool_hooks.clear()
        self.post_tool_hooks.clear()

    async def run_pre_tool(
        self, tool_name: str, tool_args: dict, context: dict
    ) -> HookResult:
        """Execute all pre-tool hooks in sequence.

        If ANY hook returns allowed=False, execution stops immediately and the
        tool call is denied. Args modified by earlier hooks are passed to later
        hooks, allowing cumulative modification.
        """
        current_args = dict(tool_args)
        for hook in self.pre_tool_hooks:
            result = await hook(tool_name, current_args, context)
            if not result.allowed:
                return HookResult(allowed=False, modified_args=current_args)
            if result.modified_args:
                current_args = dict(result.modified_args)
        return HookResult(allowed=True, modified_args=current_args)

    async def run_post_tool(
        self, tool_name: str, tool_args: dict, result: str, context: dict
    ) -> None:
        """Execute all post-tool hooks in sequence.

        Post-tool hooks are fire-and-forget — exceptions are silently caught
        so they never break the main execution flow.
        """
        for hook in self.post_tool_hooks:
            try:
                await hook(tool_name, tool_args, result, context)
            except Exception:
                pass  # Post-tool hooks must never break the harness flow


# Global singleton instance
hook_manager = HookManager()
