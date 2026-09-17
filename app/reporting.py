import json
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ---------------------------------------------------------
# REPORT DIRECTORY
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(REPORTS_DIR, exist_ok=True)


# ---------------------------------------------------------
# FILE NAME
# ---------------------------------------------------------

def make_report_name(extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"responsible_ai_report_{timestamp}.{extension}"


# ---------------------------------------------------------
# JSON REPORT
# ---------------------------------------------------------

def save_json(results, summary):
    filename = make_report_name("json")
    path = os.path.join(REPORTS_DIR, filename)

    report_data = {
        "project": "Responsible AI System",
        "title": "Bias Detection + Explainability Report",
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "results": results,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    return filename


# ---------------------------------------------------------
# HTML REPORT
# ---------------------------------------------------------

def save_html(results, summary):
    filename = make_report_name("html")
    path = os.path.join(REPORTS_DIR, filename)

    generated_at = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")

    def esc(value):
        value = str(value if value is not None else "")
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;")
        )

    overall_risk = summary.get("overall_risk", "N/A")
    total = summary.get("total", len(results))
    avg_bias = summary.get("avg_bias", 0)
    avg_toxicity = summary.get("avg_toxicity", 0)
    avg_hallucination = summary.get("avg_hallucination", 0)
    avg_fairness = summary.get("avg_fairness", 0)

    rows = ""

    for index, result in enumerate(results, start=1):
        evaluation = result.get("evaluation", {})

        explanation = evaluation.get("explanation", [])
        mitigation = evaluation.get("mitigation", [])

        explanation_html = "".join(
            f"<li>{esc(item)}</li>" for item in explanation
        )

        mitigation_html = "".join(
            f"<li>{esc(item)}</li>" for item in mitigation
        )

        rows += f"""
        <div class="evaluation">
            <h2>Evaluation {index}</h2>

            <table>
                <tr>
                    <th>Provider</th>
                    <td>{esc(result.get("provider_label", result.get("provider", "")))}</td>
                </tr>

                <tr>
                    <th>Model</th>
                    <td>{esc(result.get("model", ""))}</td>
                </tr>

                <tr>
                    <th>Latency</th>
                    <td>{esc(result.get("latency_ms", 0))} ms</td>
                </tr>

                <tr>
                    <th>Risk Level</th>
                    <td>
                        <span class="risk {esc(str(evaluation.get("risk_level", "N/A")).lower())}">
                            {esc(evaluation.get("risk_level", "N/A"))}
                        </span>
                    </td>
                </tr>

                <tr>
                    <th>Overall Risk</th>
                    <td>{esc(evaluation.get("overall_risk_score", 0))}%</td>
                </tr>

                <tr>
                    <th>Bias</th>
                    <td>{esc(evaluation.get("bias", 0))}%</td>
                </tr>

                <tr>
                    <th>Toxicity</th>
                    <td>{esc(evaluation.get("toxicity", 0))}%</td>
                </tr>

                <tr>
                    <th>Hallucination</th>
                    <td>{esc(evaluation.get("hallucination", 0))}%</td>
                </tr>

                <tr>
                    <th>Fairness</th>
                    <td>{esc(evaluation.get("fairness", 0))}%</td>
                </tr>
            </table>

            <h3>Prompt</h3>
            <div class="box">{esc(result.get("prompt", ""))}</div>

            <h3>Model Response</h3>
            <div class="box">{esc(result.get("response", ""))}</div>

            <h3>Why Flagged</h3>
            <ul>
                {explanation_html or "<li>No specific issues were detected.</li>"}
            </ul>

            <h3>Recommended Mitigation</h3>
            <ul>
                {mitigation_html or "<li>No mitigation recommendations were generated.</li>"}
            </ul>
        </div>
        """

    html = f"""<!doctype html>
<html lang="en">

<head>
<meta charset="utf-8">

<title>Responsible AI Evaluation Report</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 40px;
    background: #f4f6f8;
    color: #172033;
    font-family: Arial, Helvetica, sans-serif;
    line-height: 1.6;
}}

.container {{
    max-width: 1050px;
    margin: auto;
    background: white;
    padding: 45px;
    border-radius: 18px;
    box-shadow: 0 10px 35px rgba(0,0,0,.08);
}}

.header {{
    text-align: center;
    border-bottom: 2px solid #e8ecf2;
    padding-bottom: 25px;
    margin-bottom: 30px;
}}

.header h1 {{
    margin: 0;
    font-size: 32px;
}}

.header p {{
    margin: 8px 0;
    color: #697386;
}}

.summary {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 35px;
}}

.metric {{
    background: #f7f9fc;
    border: 1px solid #e5e9f0;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
}}

.metric span {{
    display: block;
    color: #697386;
    font-size: 13px;
}}

.metric strong {{
    display: block;
    font-size: 25px;
    margin-top: 5px;
}}

.overall {{
    background: #f7f9fc;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 35px;
    text-align: center;
}}

.overall h2 {{
    margin: 0 0 8px;
}}

.risk {{
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: bold;
}}

.risk.low {{
    background: #dff5e5;
    color: #177245;
}}

.risk.medium {{
    background: #fff1c7;
    color: #8a6200;
}}

.risk.high {{
    background: #ffe0e0;
    color: #a32121;
}}

.evaluation {{
    border-top: 2px solid #e8ecf2;
    padding-top: 30px;
    margin-top: 35px;
}}

.evaluation h2 {{
    margin-top: 0;
}}

h3 {{
    margin-top: 25px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0 25px;
}}

th,
td {{
    border: 1px solid #e1e5eb;
    padding: 11px;
    text-align: left;
    vertical-align: top;
}}

th {{
    width: 180px;
    background: #f7f9fc;
}}

.box {{
    background: #f7f9fc;
    border: 1px solid #e2e7ef;
    border-radius: 10px;
    padding: 16px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}}

.footer {{
    margin-top: 45px;
    padding-top: 20px;
    border-top: 1px solid #e5e9f0;
    text-align: center;
    color: #7a8495;
    font-size: 13px;
}}

@media(max-width: 800px) {{
    body {{
        padding: 15px;
    }}

    .container {{
        padding: 25px;
    }}

    .summary {{
        grid-template-columns: 1fr 1fr;
    }}
}}

</style>

</head>

<body>

<div class="container">

    <div class="header">
        <h1>Responsible AI System</h1>
        <h2>Bias Detection + Explainability Report</h2>
        <p>Generated on {esc(generated_at)}</p>
    </div>

    <div class="overall">
        <h2>Overall Risk Level</h2>
        <span class="risk {esc(str(overall_risk).lower())}">
            {esc(overall_risk)}
        </span>
        <p>{total} evaluation(s) included in this report.</p>
    </div>

    <div class="summary">

        <div class="metric">
            <span>Total Requests</span>
            <strong>{total}</strong>
        </div>

        <div class="metric">
            <span>Bias</span>
            <strong>{avg_bias}%</strong>
        </div>

        <div class="metric">
            <span>Toxicity</span>
            <strong>{avg_toxicity}%</strong>
        </div>

        <div class="metric">
            <span>Hallucination</span>
            <strong>{avg_hallucination}%</strong>
        </div>

        <div class="metric">
            <span>Fairness</span>
            <strong>{avg_fairness}%</strong>
        </div>

    </div>

    <h2>Evaluation Details</h2>

    {rows}

    <div class="footer">
        Responsible AI System — Bias Detection + Explainability Dashboard
    </div>

</div>

</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    return filename


# ---------------------------------------------------------
# PDF REPORT
# ---------------------------------------------------------

def save_pdf(results, summary):
    filename = make_report_name("pdf")
    path = os.path.join(REPORTS_DIR, filename)

    generated_at = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="Responsible AI Evaluation Report",
        author="Responsible AI System",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#667085"),
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceBefore=16,
        spaceAfter=10,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Responsible AI System",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Bias Detection + Explainability Report",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"Generated on {generated_at}",
            subtitle_style
        )
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    overall_risk = summary.get("overall_risk", "N/A")
    total = summary.get("total", len(results))

    avg_bias = summary.get("avg_bias", 0)
    avg_toxicity = summary.get("avg_toxicity", 0)
    avg_hallucination = summary.get("avg_hallucination", 0)
    avg_fairness = summary.get("avg_fairness", 0)

    story.append(
        Paragraph(
            "Overall Evaluation Summary",
            heading_style
        )
    )

    summary_data = [
        [
            Paragraph("<b>Metric</b>", small_style),
            Paragraph("<b>Value</b>", small_style),
        ],
        [
            Paragraph("Total Requests", small_style),
            Paragraph(str(total), small_style),
        ],
        [
            Paragraph("Overall Risk Level", small_style),
            Paragraph(str(overall_risk), small_style),
        ],
        [
            Paragraph("Average Bias", small_style),
            Paragraph(f"{avg_bias}%", small_style),
        ],
        [
            Paragraph("Average Toxicity", small_style),
            Paragraph(f"{avg_toxicity}%", small_style),
        ],
        [
            Paragraph("Average Hallucination", small_style),
            Paragraph(f"{avg_hallucination}%", small_style),
        ],
        [
            Paragraph("Average Fairness Risk", small_style),
            Paragraph(f"{avg_fairness}%", small_style),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[75 * mm, 75 * mm],
        repeatRows=1,
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9dee7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(summary_table)
    story.append(Spacer(1, 12))

    # -----------------------------------------------------
    # RISK GUIDE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Risk Interpretation",
            heading_style
        )
    )

    risk_data = [
        [
            Paragraph("<b>Risk Level</b>", small_style),
            Paragraph("<b>Range</b>", small_style),
            Paragraph("<b>Interpretation</b>", small_style),
        ],
        [
            Paragraph("Low", small_style),
            Paragraph("0–29%", small_style),
            Paragraph("Generally safe", small_style),
        ],
        [
            Paragraph("Medium", small_style),
            Paragraph("30–59%", small_style),
            Paragraph("Needs attention", small_style),
        ],
        [
            Paragraph("High", small_style),
            Paragraph("60–100%", small_style),
            Paragraph("Needs review", small_style),
        ],
    ]

    risk_table = Table(
        risk_data,
        colWidths=[40 * mm, 35 * mm, 75 * mm],
        repeatRows=1,
    )

    risk_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9dee7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ])
    )

    story.append(risk_table)

    # -----------------------------------------------------
    # INDIVIDUAL RESULTS
    # -----------------------------------------------------

    for index, result in enumerate(results, start=1):

        evaluation = result.get("evaluation", {})

        story.append(PageBreak())

        story.append(
            Paragraph(
                f"Evaluation {index}",
                heading_style
            )
        )

        provider = result.get(
            "provider_label",
            result.get("provider", "Unknown")
        )

        model = result.get("model", "Unknown")
        latency = result.get("latency_ms", 0)

        risk_level = evaluation.get("risk_level", "N/A")
        overall_score = evaluation.get("overall_risk_score", 0)

        bias = evaluation.get("bias", 0)
        toxicity = evaluation.get("toxicity", 0)
        hallucination = evaluation.get("hallucination", 0)
        fairness = evaluation.get("fairness", 0)

        details = [
            [
                Paragraph("<b>Field</b>", small_style),
                Paragraph("<b>Value</b>", small_style),
            ],
            [
                Paragraph("Provider", small_style),
                Paragraph(str(provider), small_style),
            ],
            [
                Paragraph("Model", small_style),
                Paragraph(str(model), small_style),
            ],
            [
                Paragraph("Risk Level", small_style),
                Paragraph(str(risk_level), small_style),
            ],
            [
                Paragraph("Overall Risk", small_style),
                Paragraph(f"{overall_score}%", small_style),
            ],
            [
                Paragraph("Bias", small_style),
                Paragraph(f"{bias}%", small_style),
            ],
            [
                Paragraph("Toxicity", small_style),
                Paragraph(f"{toxicity}%", small_style),
            ],
            [
                Paragraph("Hallucination", small_style),
                Paragraph(f"{hallucination}%", small_style),
            ],
            [
                Paragraph("Fairness", small_style),
                Paragraph(f"{fairness}%", small_style),
            ],
            [
                Paragraph("Latency", small_style),
                Paragraph(f"{latency} ms", small_style),
            ],
        ]

        details_table = Table(
            details,
            colWidths=[55 * mm, 95 * mm],
            repeatRows=1,
        )

        details_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f7")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9dee7")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ])
        )

        story.append(details_table)

        # Prompt

        story.append(
            Paragraph(
                "Test Prompt",
                heading_style
            )
        )

        prompt = str(result.get("prompt", ""))

        story.append(
            Paragraph(
                prompt.replace("&", "&amp;")
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace("\n", "<br/>"),
                body_style
            )
        )

        # Response

        story.append(
            Paragraph(
                "Model Response",
                heading_style
            )
        )

        response = str(result.get("response", ""))

        story.append(
            Paragraph(
                response.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace("\n", "<br/>"),
                body_style
            )
        )

        # Explanation

        story.append(
            Paragraph(
                "Why the Response Was Flagged",
                heading_style
            )
        )

        explanation = evaluation.get("explanation", [])

        if explanation:
            for item in explanation:
                safe_item = (
                    str(item)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                story.append(
                    Paragraph(
                        f"• {safe_item}",
                        body_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No specific issues were detected.",
                    body_style
                )
            )

        # Mitigation

        story.append(
            Paragraph(
                "Recommended Mitigation",
                heading_style
            )
        )

        mitigation = evaluation.get("mitigation", [])

        if mitigation:
            for item in mitigation:
                safe_item = (
                    str(item)
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                story.append(
                    Paragraph(
                        f"• {safe_item}",
                        body_style
                    )
                )
        else:
            story.append(
                Paragraph(
                    "No mitigation recommendations were generated.",
                    body_style
                )
            )

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    doc.build(story)

    return filename