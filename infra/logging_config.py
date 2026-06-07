"""Logging configuration for the agent harness."""

import os
import sys
import logging

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler(os.sys.stdout) if os.getenv("DEBUG") else logging.NullHandler()
    ]
)
logger = logging.getLogger("agent-harness")
