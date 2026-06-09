"""Unit tests for core/model_config.py — model configuration and caching."""

import os
import pytest
from unittest.mock import patch, MagicMock
from core.model_config import get_model, _MODEL_CACHE


class TestGetModel:
    """Test model initialization and caching."""

    def test_returns_model_instance(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_model = MagicMock()
            mock_init.return_value = mock_model
            with patch.dict(os.environ, {"AI_PROVIDER": "openrouter", "AI_MODEL": "test/model", "OPENROUTER_API_KEY": "test-key"}):
                result = get_model()
                assert result is mock_model
                mock_init.assert_called_once()

    def test_caches_model(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_model = MagicMock()
            mock_init.return_value = mock_model
            with patch.dict(os.environ, {"AI_PROVIDER": "openrouter", "AI_MODEL": "test/model", "OPENROUTER_API_KEY": "test-key"}):
                result1 = get_model()
                result2 = get_model()
                assert result1 is result2
                assert mock_init.call_count == 1

    def test_different_providers_different_cache(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_model = MagicMock()
            mock_init.return_value = mock_model
            with patch.dict(os.environ, {"AI_PROVIDER": "openrouter", "AI_MODEL": "model-a", "OPENROUTER_API_KEY": "key-a"}):
                get_model()
            with patch.dict(os.environ, {"AI_PROVIDER": "openai", "AI_MODEL": "model-b"}):
                get_model()
            assert mock_init.call_count == 2

    def test_openrouter_sets_base_url(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_init.return_value = MagicMock()
            with patch.dict(os.environ, {"AI_PROVIDER": "openrouter", "AI_MODEL": "test/model", "OPENROUTER_API_KEY": "test-key"}):
                get_model()
                call_kwargs = mock_init.call_args[1]
                assert call_kwargs["base_url"] == "https://openrouter.ai/api/v1"
                assert call_kwargs["api_key"] == "test-key"

    def test_ollama_sets_base_url(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_init.return_value = MagicMock()
            with patch.dict(os.environ, {"AI_PROVIDER": "ollama", "AI_MODEL": "llama3", "OLLAMA_BASE_URL": "http://test-ollama:11434"}):
                get_model()
                call_kwargs = mock_init.call_args[1]
                assert call_kwargs["base_url"] == "http://test-ollama:11434"
                assert call_kwargs["model_provider"] == "ollama"

    def test_default_values(self):
        _MODEL_CACHE.clear()
        with patch("core.model_config.init_chat_model") as mock_init:
            mock_init.return_value = MagicMock()
            env = {k: v for k, v in os.environ.items() if k not in ("AI_PROVIDER", "AI_MODEL", "OPENROUTER_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                os.environ.pop("AI_PROVIDER", None)
                os.environ.pop("AI_MODEL", None)
                get_model()
                mock_init.assert_called_once()
