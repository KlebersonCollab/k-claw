"""AI model configuration and caching."""

import os
from langchain.chat_models import init_chat_model

# Global cache for the model instance
_MODEL_CACHE: dict = {}


def get_model():
    """Get or create a cached chat model instance.

    Returns:
        A chat model instance configured based on environment variables.

    Environment Variables:
        AI_PROVIDER: The model provider (default: "openai")
        AI_MODEL: The model name (default: "gpt-4o")
        OPENROUTER_API_KEY: API key for OpenRouter (if provider is "openrouter")
    """
    provider = os.getenv("AI_PROVIDER", "openrouter")
    model_name = os.getenv("AI_MODEL", "openrouter/owl-alpha")
    cache_key = f"{provider}:{model_name}"

    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    kwargs = {}
    if provider == "openrouter":
        kwargs["base_url"] = "https://openrouter.ai/api/v1"
        kwargs["api_key"] = os.getenv("OPENROUTER_API_KEY")
        provider = "openai"

    model = init_chat_model(model_name, model_provider=provider, **kwargs)
    _MODEL_CACHE[cache_key] = model
    return model
