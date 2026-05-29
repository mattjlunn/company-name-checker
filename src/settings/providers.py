"""Enhanced provider support with direct integrations for OpenRouter, OpenAI, and Ollama."""

from typing import Optional, Union

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from src.settings.config import Settings, load_settings


def get_llm_model(
    model_id: Optional[str] = None,
) -> Union[OpenAIChatModel, OpenRouterModel]:
    """
    Get model with proper provider integration.

    Args:
        model_id: Optional string in format "provider:model_name".
                  If None, falls back to the .env default_llm_model.
    """
    print(f"Get model for {model_id}")
    settings = load_settings()
    for k, v in settings:
        print(f"{k}: {v}")

    # 1. Determine which string to use (user input vs. default)
    full_model_string = model_id if model_id else settings.default_llm_model
    print(f"Selected model: {full_model_string}")
    # 2. Extract the provider and the actual model name
    if ":" not in full_model_string:
        raise ValueError(
            f"Invalid model string: '{full_model_string}'. "
            "Expected format is 'provider:model' (e.g., 'openrouter:gpt-4o-mini')."
        )

    provider, model_name = full_model_string.split(":", 1)

    # 3. Route to the correct factory function
    if provider == "openrouter":
        print("Using OpenRouter model")
        return _create_openrouter_model(settings, model_name)
    elif provider == "openai":
        print("Using OpenAI model")
        return _create_openai_model(settings, model_name)
    elif provider == "ollama":
        print("Using Ollama model")
        return _create_ollama_model(settings, model_name)
    else:
        raise ValueError(f"Unsupported provider derived from string: {provider}")


def _create_openrouter_model(settings: Settings, model_name: str) -> OpenRouterModel:
    """
    Create OpenRouter model with direct integration and app attribution.
    Supports OpenRouter-specific features like app attribution for analytics.

    Args:
        settings: Application settings

    Returns:
        Configured OpenRouter model
    """
    provider = OpenRouterProvider(
        api_key=settings.openrouter_api_key,
        app_url=settings.openrouter_app_url,
        app_title=settings.openrouter_app_title,
    )
    return OpenRouterModel(model_name, provider=provider)


def _create_openai_model(settings: Settings, model_name: str) -> OpenAIChatModel:
    """
    Create OpenAI model with direct integration.

    Args:
        settings: Application settings

    Returns:
        Configured OpenAI model
    """
    provider = OpenAIProvider(api_key=settings.llm_api_key)
    return OpenAIChatModel(model_name, provider=provider)


def _create_ollama_model(settings: Settings, model_name: str) -> OpenAIChatModel:
    """
    Create Ollama model via OpenAI-compatible API.

    Ollama provides an OpenAI-compatible API endpoint.

    Args:
        settings: Application settings

    Returns:
        Configured Ollama model via OpenAI provider
    """
    provider = OpenAIProvider(
        base_url=settings.llm_base_url or "http://localhost:11434/v1",
        api_key="ollama",  # Required but unused by Ollama
    )
    return OpenAIChatModel(model_name, provider=provider)
