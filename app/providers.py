import os
import time
import requests

PROVIDERS = {
    "openai": {
        "label": "OpenAI / ChatGPT",
        "env": "OPENAI_API_KEY",
        "default_model": "gpt-5",
        "models": ["gpt-5", "gpt-5-mini"],
        "paid": True,
    },
    "groq": {
        "label": "Groq",
        "env": "GROQ_API_KEY",
        "default_model": "openai/gpt-oss-20b",
        "models": ["openai/gpt-oss-20b", "llama-3.3-70b-versatile"],
        "paid": True,
    },
    "anthropic": {
        "label": "Anthropic / Claude",
        "env": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-5-20250929",
        "models": ["claude-sonnet-4-5-20250929"],
        "paid": True,
    },
    "gemini": {
        "label": "Google Gemini",
        "env": "GEMINI_API_KEY",
        "default_model": "gemini-3.8-flash",
        "models": ["gemini-3.8-flash"],
        "paid": True,
    },
    "ollama": {
        "label": "Ollama (local/free)",
        "env": "OLLAMA_BASE_URL",
        "default_model": "gemma3",
        "models": ["llama3.2","gemma3", "qwen3"],
        "paid": False,
    },
    "openrouter": {
        "label": "OpenRouter",
        "env": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-oss-20b:free",
        "models": ["openai/gpt-oss-20b:free", "meta-llama/llama-3.3-70b-instruct:free"],
        "paid": True,
    },
    "deepseek": {
        "label": "DeepSeek",
        "env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat"],
        "paid": True,
    },
    "mistral": {
        "label": "Mistral",
        "env": "MISTRAL_API_KEY",
        "default_model": "mistral-small-latest",
        "models": ["mistral-small-latest"],
        "paid": True,
    },
    "together": {
        "label": "Together AI",
        "env": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo"],
        "paid": True,
    },
}

def _key(provider, supplied):
    return supplied or os.getenv(PROVIDERS[provider]["env"], "")

def _openai_compatible(provider, model, prompt, api_key, base_url):
    if not api_key:
        raise RuntimeError(f"{PROVIDERS[provider]['label']} API key is missing.")
    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url=base_url)
    start = time.perf_counter()
    response = client.responses.create(model=model, input=prompt)
    latency_ms = round((time.perf_counter() - start) * 1000, 2)
    text = getattr(response, "output_text", "") or ""
    usage = getattr(response, "usage", None)
    return text, latency_ms, {
        "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
        "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
    }

def run_model(provider, model, prompt, api_key=None):
    model = model or PROVIDERS[provider]["default_model"]

    if provider == "openai":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key), None)

    if provider == "groq":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key),
                                  "https://api.groq.com/openai/v1")

    if provider == "openrouter":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key),
                                  "https://openrouter.ai/api/v1")

    if provider == "deepseek":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key),
                                  "https://api.deepseek.com")

    if provider == "mistral":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key),
                                  "https://api.mistral.ai/v1")

    if provider == "together":
        return _openai_compatible(provider, model, prompt, _key(provider, api_key),
                                  "https://api.together.xyz/v1")

    if provider == "anthropic":
        key = _key(provider, api_key)
        if not key:
            raise RuntimeError("Anthropic API key is missing.")
        from anthropic import Anthropic
        client = Anthropic(api_key=key)
        start = time.perf_counter()
        msg = client.messages.create(
            model=model, max_tokens=1200,
            messages=[{"role": "user", "content": prompt}]
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        text = "".join(getattr(block, "text", "") for block in msg.content)
        usage = getattr(msg, "usage", None)
        return text, latency_ms, {
            "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
            "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
        }

    if provider == "gemini":
        key = _key(provider, api_key)
        if not key:
            raise RuntimeError("Gemini API key is missing.")
        from google import genai
        client = genai.Client(api_key=key)
        start = time.perf_counter()
        interaction = client.interactions.create(model=model, input=prompt)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        text = getattr(interaction, "output_text", "") or ""
        return text, latency_ms, {}

    if provider == "ollama":
        base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        start = time.perf_counter()
        r = requests.post(
            f"{base}/api/chat",
            json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=180,
        )
        r.raise_for_status()
        data = r.json()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        msg = data.get("message", {})
        return msg.get("content", ""), latency_ms, {
            "input_tokens": data.get("prompt_eval_count"),
            "output_tokens": data.get("eval_count"),
        }

    raise RuntimeError(f"Unknown provider: {provider}")
