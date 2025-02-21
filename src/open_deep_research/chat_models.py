def init_chat_model(model: str, model_provider: str, temperature: float = None):
    """Initialize a chat model with the given provider and settings.
    
    Args:
        model: The model name/ID
        model_provider: The provider (openai, anthropic, groq)
        temperature: Temperature setting (some models don't support this)
    """
    # List of models that don't support temperature
    no_temp_models = {"gpt-4o", "o3-mini", "mixtral-8x7b", "llama2-70b"}
    
    if model_provider == "openai":
        if model.lower() in no_temp_models:
            return ChatOpenAI(model=model)
        else:
            return ChatOpenAI(
                model=model,
                temperature=temperature if temperature is not None else 0
            )
    elif model_provider == "anthropic":
        # Anthropic models support temperature
        return ChatAnthropic(
            model=model,
            temperature=temperature if temperature is not None else 0
        )
    elif model_provider == "groq":
        # Groq models don't support temperature
        return ChatGroq(
            model=model
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")