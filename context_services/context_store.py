from typing import Any, Dict, Optional
from .stm_manager import STMManager # Assuming relative import within package

# --- Mocking LTM for isolation and testability ---
class LTMMockStore:
    """
    Mock representation of the Long-Term Memory (LTM) store.
    In a real system, this would interface with a vector database or knowledge graph.
    """
    def __init__(self):
        # LTM stores persistent global context knowledge
        self._knowledge_base: Dict[str, Any] = {
            "system_initialization": True,
            "core_protocol": "CAS v1.0 Active"
        }

    def query_knowledge(self, query: str) -> Optional[Dict[str, str]]:
        """Simulates querying LTM for relevant knowledge based on a string query."""
        print(f"[LTM] Querying Knowledge Base for: '{query}'...")
        if "protocol" in query.lower():
            return {"source": "CAS Design Report", "content": "The CAS operates under strict protocol guidelines."}
        elif "user_intent" in query.lower():
            return {"source": "Historical Logs", "content": "User intent is always task completion."}
        else:
            # Simulate no match or general fallback retrieval
            return None

    def persist_memory(self, key: str, value: Any) -> bool:
        """Simulates persisting new memory to LTM."""
        if isinstance(key, str) and value is not None:
            print(f"[LTM] Persisting new memory: {key}")
            self._knowledge_base[key] = value
            return True
        return False

class ContextStore:
    """
    The ContextStore acts as the single source of truth (SSOT) for context. 
    It orchestrates interactions between Short-Term Memory (STM) and 
    Long-Term Memory (LTM), ensuring atomic retrieval/persistence of 'Query Context'.

    Adheres to the Facade pattern, simplifying access across system components.
    """

    def __init__(self):
        # Dependency Injection: Use the singleton STMManager and the mock LTM store
        self._stm: STMManager = STMManager()
        self._ltm: LTMMockStore = LTMMockStore()
        print("[ContextStore] Initialized. Ready to manage context flow.")

    def query_context(self, query: str) -> Dict[str, Any]:
        """
        Retrieves the holistic contextual understanding (Query Context).

        This involves reading short-term operational state and enriching it 
        with relevant long-term knowledge based on the input query.

        Args:
            query: The user's raw input or current focus of inquiry.

        Returns:
            A dictionary containing the combined context (STM snapshot + LTM findings).
        """
        # 1. Capture immediate operational state (STM) - Atomic Read
        stm_snapshot = self._stm.get_all_states()

        # 2. Query long-term knowledge base (LTM)
        ltm_knowledge = self._ltm.query_knowledge(query)

        # 3. Combine and structure the context object
        context: Dict[str, Any] = {
            "raw_query": query,
            "stm_snapshot": stm_snapshot, # Short-Term Context (Operational State)
            "ltm_retrieval": ltm_knowledge if ltm_knowledge else {"source": "None", "content": "No specific long-term context found."} # Long-Term Context (Knowledge Base)
        }

        return context

    def update_context(self, key: str, value: Any):
        """
        Updates both the Short-Term Memory and persists the change to 
        the Long-Term Memory if deemed important enough for persistence.
        
        This method encapsulates an atomic WRITE operation across contexts.
        
        Args:
            key: The key describing the context element (e.g., 'user_goal').
            value: The new data value.
        """
        print(f"--- [ContextStore] Attempting to update context: {key} ---")

        # 1. Update STM immediately (Short-Term)
        self._stm.set_state(key, value)

        # 2. Persist the update to LTM (Long-Term) - Critical step
        success = self._ltm.persist_memory(key, value)
        if success:
            print("Context persistence successful across STM and LTM.")
        else:
            print("WARNING: Failed to persist context to LTM.")

# Example usage (for demonstration purposes):
if __name__ == "__main__":
    context_store = ContextStore()
    
    # --- Test Read Flow ---
    user_query = "Qual é o protocolo operacional do sistema?"
    initial_context = context_store.query_context(user_query)

    print("\n" + "="*50)
    print("QUERY CONTEXT RESULT:")
    import json
    print(json.dumps(initial_context, indent=4))
    print("="*50)

    # --- Test Write Flow (Atomic Update) ---
    new_goal = "Desenvolver os módulos de contexto."
    context_store.update_context("user_goal", new_goal)

    # Verify the write was effective in both layers
    updated_context = context_store.query_context("Verificar meta do usuário")

    print("\n" + "="*50)
    print("UPDATED CONTEXT RESULT (Verification):")
    print(f"New user_goal in STM snapshot: {updated_context['stm_snapshot'].get('user_goal')}")
    print(f"New user_goal persisted in LTM retrieval keys: {'user_goal' in updated_context['ltm_retrieval']}")
    print("="*50)