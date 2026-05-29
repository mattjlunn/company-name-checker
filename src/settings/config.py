from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Configuration (OpenAI-compatible)
    # llm_provider: Literal["openrouter", "openai", "ollama"] = Field(
    #    default="openrouter", description="LLM provider to use"
    # )

    default_llm_model: str = Field(
        default="openrouter:openai/gpt-4o-mini",
        description="Default provider:model string to use",
    )

    # OpenRouter-Specific (Optional)
    openrouter_app_url: Optional[str] = Field(
        default=None, description="App URL for OpenRouter analytics (optional)"
    )
    openrouter_app_title: Optional[str] = Field(
        default=None, description="App title for OpenRouter tracking (optional)"
    )

    openrouter_api_key: str = Field(..., description="API key for OpenRouter")


def load_settings() -> Settings:
    """Load settings with proper error handling."""
    try:
        return Settings()
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        raise ValueError(error_msg) from e
