"""Schema de ferramentas e registro global (singleton)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ToolDescriptor(BaseModel):
    name: str
    description: str
    permissions_required: str
    handler: Any
    requires_approval: bool = False


class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDescriptor] = {}

    def register(
        self,
        name: str,
        description: str,
        permissions: str,
        handler: Any,
        requires_approval: bool = False,
    ):
        self.tools[name] = ToolDescriptor(
            name=name,
            description=description,
            permissions_required=permissions,
            handler=handler,
            requires_approval=requires_approval,
        )

    def get_langchain_tools(self, current_permissions: str) -> List[Any]:
        return [
            desc.handler
            for desc in self.tools.values()
            if self._has_permission(current_permissions, desc.permissions_required)
        ]

    def _has_permission(self, current: str, required: str) -> bool:
        hierarchy = {"read": 1, "write": 2, "execute": 3}
        return hierarchy.get(current, 0) >= hierarchy.get(required, 0)


# ── Singleton global ──────────────────────────────────────────────────────────
registry = ToolRegistry()

# --- Global Reference for Delegation (Late Binding) ---
_HARNESS_REF: Any = None


def set_harness_refs(h_ref):
    global _HARNESS_REF
    _HARNESS_REF = h_ref
