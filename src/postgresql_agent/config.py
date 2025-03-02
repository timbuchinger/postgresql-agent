"""Configuration settings for the PostgreSQL agent."""

# LLM Configuration
LLM_PROVIDER = "litellm"
LLM_MODEL = ("groq/qwen-2.5-32b",)  # Using standard litellm model format
LLM_DEFAULT_PARAMS = {"temperature": 0.7, "max_tokens": 2000}
