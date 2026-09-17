from flask import Blueprint, jsonify, render_template, request, send_from_directory
from .providers import PROVIDERS, run_model
from .evaluator import evaluate, summarize
from .reporting import save_json, save_html, save_pdf

import os


bp = Blueprint("main", __name__)


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------

@bp.get("/")
def index():
    return render_template(
        "index.html",
        providers=PROVIDERS
    )


# ---------------------------------------------------------
# PROVIDERS API
# ---------------------------------------------------------

@bp.get("/api/providers")
def providers():
    return jsonify(PROVIDERS)


# ---------------------------------------------------------
# RUN MODEL + EVALUATION
# ---------------------------------------------------------

@bp.post("/api/run")
def run():

    data = request.get_json(force=True) or {}

    provider = data.get("provider", "ollama")

    model = (
        data.get("model")
        or PROVIDERS.get(provider, {}).get("default_model")
    )

    prompt = (data.get("prompt") or "").strip()

    api_key = data.get("api_key") or None

    reference = data.get("reference") or None

    # Validate provider

    if provider not in PROVIDERS:
        return jsonify({
            "error": "Unsupported provider"
        }), 400

    # Validate prompt

    if not prompt:
        return jsonify({
            "error": "Prompt is required"
        }), 400

    try:

        # Run selected LLM

        text, latency, usage = run_model(
            provider,
            model,
            prompt,
            api_key
        )

        # Evaluate response

        evaluation = evaluate(
            prompt,
            text,
            reference
        )

        result = {
            "provider": provider,

            "provider_label": PROVIDERS[provider]["label"],

            "model": model,

            "prompt": prompt,

            "response": text,

            "latency_ms": latency,

            "usage": usage,

            "evaluation": evaluation
        }

        return jsonify(result)

    except Exception as exc:

        return jsonify({
            "error": str(exc)
        }), 502


# ---------------------------------------------------------
# GENERATE REPORTS
# ---------------------------------------------------------

@bp.post("/api/report")
def report():

    try:

        data = request.get_json(force=True) or {}

        results = data.get("results", [])

        if not results:

            return jsonify({
                "error": "No evaluation results were provided."
            }), 400

        # Create summary

        summary = summarize(results)

        # Generate all three report formats

        json_name = save_json(
            results,
            summary
        )

        html_name = save_html(
            results,
            summary
        )

        pdf_name = save_pdf(
            results,
            summary
        )

        return jsonify({

            "success": True,

            "summary": summary,

            "json_url": f"/reports/{json_name}",

            "html_url": f"/reports/{html_name}",

            "pdf_url": f"/reports/{pdf_name}"

        })

    except Exception as exc:

        print("REPORT GENERATION ERROR:", exc)

        return jsonify({
            "error": f"Could not generate report: {str(exc)}"
        }), 500


# ---------------------------------------------------------
# SERVE GENERATED REPORT FILES
# ---------------------------------------------------------

@bp.get("/reports/<path:name>")
def report_file(name):

    reports_dir = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        ),
        "reports"
    )

    return send_from_directory(
        reports_dir,
        name,
        as_attachment=False
    )