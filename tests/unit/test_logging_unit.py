import pytest
import logging
from infra.logging_config import logger

def test_logger_initialization():
    assert logger.name == "agent-harness"
    # Logger exists and is active
    assert logger is not None
