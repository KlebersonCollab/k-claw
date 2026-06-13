import threading
from typing import Any, Dict, Optional

class STMManager:
    """
    Short-Term Memory Manager (STM).

    Implements a Singleton pattern to manage the immediate operational state 
    of the agent during a single task execution.

    Attributes:
        _state: Dictionary holding the current operational state {key: value}.
    """

    # Class variable used to enforce the Singleton pattern
    _instance = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls):
        """Ensures only one instance of STMManager exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    # Use the parent class constructor for Singleton behavior
                    cls._instance = super(STMManager, cls).__new__(cls)
                    # Initialize internal state only once
                    cls._instance._state: Dict[str, Any] = {}
        return cls._instance

    def set_state(self, key: str, value: Any) -> None:
        """
        Sets or updates a piece of operational state.

        Args:
            key: The unique identifier for the state (e.g., 'current_step').
            value: The data associated with the state.
        """
        if key is None or value is None:
            raise ValueError("Key and value must not be None.")
        self._state[key] = value
        print(f"[STMManager] State set: {key} = {value}") # Added logging for clarity

    def get_state(self, key: str) -> Optional[Any]:
        """
        Retrieves the operational state associated with a given key.

        Args:
            key: The unique identifier of the state to retrieve.

        Returns:
            The stored value if the key exists, otherwise None.
        """
        return self._state.get(key)

    def get_all_states(self) -> Dict[str, Any]:
        """
        Retrieves a copy of all currently stored states.
        
        Returns:
            A dictionary containing all key-value pairs in the STM.
        """
        return self._state.copy()

    def clear_state(self) -> None:
        """Clears all operational state, typically called at the end 
           of a task execution."""
        self._state.clear()
        print("[STMManager] State cleared.")

# Example usage (for demonstration purposes, not part of library code):
if __name__ == "__main__":
    stm1 = STMManager()
    stm2 = STMManager()
    
    print(f"Are stm1 and stm2 the same instance? {stm1 is stm2}")

    # Set state
    stm1.set_state("user_id", 1001)
    stm1.set_state("session_start", "2023-10-27T10:00:00")

    # Get state
    user_id = stm1.get_state("user_id")
    print(f"Retrieved user_id: {user_id}")

    # Check singleton behavior
    stm2.set_state("task_status", "running") # Updates the shared instance
    print(f"Task status via stm1 (after stm2 call): {stm1.get_state('task_status')}")

    # Clear state
    stm1.clear_state()
    print(f"User ID after clear: {stm1.get_state('user_id')}")