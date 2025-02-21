def init_chat_model(model: str, model_provider: str, temperature: float = 0):
    if model_provider == "openai":
        # For models that don't support temperature, simply skip passing it.
        if model.lower() in {"gpt-4o", "o3-mini"}:
            return ChatOpenAI(model=model)
        else:
            return ChatOpenAI(
                model=model,
                temperature=temperature
            )
    elif model_provider == "anthropic":
        # Anthropic models support temperature
        return ChatAnthropic(
            model=model,
            temperature=temperature
        )
    elif model_provider == "groq":
        # Groq models don't support temperature
        return ChatGroq(
            model=model
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_provider}")