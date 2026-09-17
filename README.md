# Responsible AI System — Bias Detection + Explainability Dashboard

This project is implemented from the uploaded project brief, whose core requirement is a quality-checker/health-dashboard for LLMs that evaluates bias, toxicity, fairness and hallucination, explains why a response was flagged, and provides mitigation ideas. The dashboard structure also preserves the brief's requested metrics, risk levels, top problems and recommended actions.

## Features

- Modern Flask + HTML/CSS dashboard.
- Provider/model selector.
- OpenAI / ChatGPT adapter.
- Groq adapter.
- Anthropic / Claude adapter.
- Google Gemini adapter.
- Ollama local/free adapter.
- OpenRouter adapter.
- DeepSeek adapter.
- Mistral adapter.
- Together AI adapter.
- Per-request API-key field plus optional `.env` configuration.
- Session-level charts.
- Heuristic bias, toxicity, fairness and hallucination-risk evaluation.
- Explainability panel.
- Full run history.
- Final HTML + JSON report.
- No API keys are hard-coded.
- Ollama can run locally without an API key.

## Important evaluation limitation

The bias/toxicity/fairness/hallucination checks are intentionally lightweight heuristics so the project is runnable without another paid "judge" LLM. A heuristic hallucination score is NOT proof that a statement is factually false. For a production system, add a trusted reference corpus/RAG verification layer and/or a separately validated evaluation model.

## Windows setup

1. Install Python 3.11+.
2. Open PowerShell in this project directory.
3. Create a virtual environment:
   `py -m venv .venv`
4. Activate it:
   `.venv\Scripts\Activate.ps1`
5. Install:
   `pip install -r requirements.txt`
6. Optional:
   `copy .env.example .env`
   and fill the API keys you actually own.
7. For Ollama, install Ollama and pull a local model, e.g.:
   `ollama pull gemma3`
8. Start the app:
   `python run.py`
9. Open:
   `http://127.0.0.1:5000`

## What you must supply yourself

- Your own provider API keys for OpenAI, Groq, Anthropic, Gemini, OpenRouter, DeepSeek, Mistral and/or Together.
- Billing/credits or a provider's available free quota where applicable.
- Ollama installation and a local model download if you want a fully local/free provider.
- Internet access for hosted APIs and the Chart.js/Google Fonts CDN used by the dashboard.
- If you need real factual hallucination verification, provide trusted reference documents/data or connect a RAG/vector-search system.

## API-key safety

Do not commit `.env` to Git. The dashboard's "Save Key in Browser" feature uses browser localStorage for convenience; it is not a secure secret vault. For a deployed production app, use server-side secrets management and HTTPS.

## Adding another OpenAI-compatible provider

Add one entry in `app/providers.py` with its environment variable, default model and base URL, then route it through `_openai_compatible`.

## Routes

- `GET /` — dashboard
- `GET /api/providers` — provider/model configuration
- `POST /api/run` — execute one model test
- `POST /api/report` — generate final HTML + JSON report
- `GET /reports/<filename>` — download a generated report

## Project mapping to the supplied brief

1. User/Test Data → prompt/reference fields.
2. LLM → selectable ChatGPT/Llama/Gemini/Claude/Ollama/etc.
3. Evaluation Engine → `app/evaluator.py`.
4. Bias / Toxicity / Hallucination checks → evaluation metrics.
5. Explainability → explanation panel.
6. Dashboard → `app/templates/index.html` + `app/static/style.css`.
7. Recommendations → Prompt Rewriting, RAG Verification, Model Routing, Additional Testing.
