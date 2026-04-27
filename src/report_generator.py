
import os
import tempfile
from datetime import datetime


def generate_pdf_report(report: dict, record_id: str) -> str:
    """Generate a PDF report and return the file path."""
    output_dir = os.path.join(tempfile.gettempdir(), "skillsense_reports")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"report_{record_id[:8]}.pdf")

    try:
        _generate_with_reportlab(report, pdf_path)
    except ImportError:
        # Fallback: simple text-based PDF via fpdf2
        try:
            _generate_with_fpdf(report, pdf_path)
        except ImportError:
            # Final fallback: plain text file
            txt_path = pdf_path.replace(".pdf", ".txt")
            with open(txt_path, "w") as f:
                f.write(_report_to_text(report))
            return txt_path

    return pdf_path


def _generate_with_reportlab(report: dict, output_path: str):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    PURPLE = colors.HexColor("#7c3aed")
    CYAN = colors.HexColor("#06b6d4")
    DARK = colors.HexColor("#1e1e2e")
    LIGHT_GRAY = colors.HexColor("#f1f5f9")
    GREEN = colors.HexColor("#10b981")
    RED = colors.HexColor("#ef4444")
    ORANGE = colors.HexColor("#f59e0b")

    title_style = ParagraphStyle("Title", parent=styles["Title"],
                                  fontSize=22, textColor=PURPLE, spaceAfter=6, alignment=TA_CENTER)
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
                               fontSize=14, textColor=PURPLE, spaceBefore=14, spaceAfter=6)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
                               fontSize=11, textColor=DARK, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
                                 fontSize=9.5, leading=14, spaceAfter=4)
    caption_style = ParagraphStyle("Caption", parent=styles["Normal"],
                                    fontSize=8.5, textColor=colors.gray, spaceAfter=2)

    story = []

    # Header
    story.append(Paragraph("KYS(Know Your Skills)", title_style))
    story.append(Paragraph("Skill Assessment &amp; Learning Plan Report", 
                            ParagraphStyle("Sub", parent=styles["Normal"], fontSize=12,
                                           textColor=CYAN, alignment=TA_CENTER, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE))
    story.append(Spacer(1, 0.3 * cm))

    # Meta info table
    meta_data = [
        ["Candidate", report.get("candidate_name", "N/A"),
         "Role", report.get("target_role", "N/A")],
        ["Date", report.get("date", datetime.now().strftime("%Y-%m-%d")),
         "Overall Score", f"{report.get('overall_score', 0)}/10"],
    ]
    meta_table = Table(meta_data, colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), PURPLE),
        ("TEXTCOLOR", (2, 0), (2, -1), PURPLE),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GRAY, colors.white]),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.4 * cm))

    # Skill Scores
    story.append(Paragraph("Skill Proficiency Scores", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.2 * cm))

    skill_scores = report.get("skill_scores", {})
    if skill_scores:
        score_rows = [["Skill", "Score", "Rating", "Evidence"]]
        for skill, data in skill_scores.items():
            score = data.get("score", 0)
            if score >= 8:
                rating, color = "Strong", GREEN
            elif score >= 6:
                rating, color = "Adequate", ORANGE
            else:
                rating, color = "Gap", RED
            score_rows.append([
                skill,
                f"{score}/10",
                rating,
                Paragraph(data.get("evidence", ""), caption_style),
            ])

        score_table = Table(score_rows, colWidths=[4 * cm, 2 * cm, 2.5 * cm, 8.5 * cm])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(score_table)

    story.append(Spacer(1, 0.4 * cm))

    # Gaps
    gaps = report.get("gaps", [])
    if gaps:
        story.append(Paragraph("Identified Skill Gaps", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
        for gap in gaps:
            story.append(Paragraph(f"• {gap}", body_style))
        story.append(Spacer(1, 0.4 * cm))

    # Learning Plan
    learning_plan = report.get("learning_plan", [])
    if learning_plan:
        story.append(Paragraph("Personalised Learning Plan", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
        story.append(Spacer(1, 0.2 * cm))

        for item in learning_plan:
            block = []
            block.append(Paragraph(
                f"<b>{item.get('skill', '')}</b> — Est. {item.get('time_estimate', 'TBD')} | Priority: {item.get('priority', 'medium')}",
                h2_style
            ))
            block.append(Paragraph(f"<i>Why:</i> {item.get('rationale', '')}", body_style))
            block.append(Paragraph("<b>Resources:</b>", body_style))
            for r in item.get("resources", []):
                block.append(Paragraph(
                    f"  • <a href='{r.get('url', '#')}' color='#7c3aed'>{r.get('title', '')}</a>"
                    f" [{r.get('type', '')}] — {r.get('duration', '')}",
                    body_style
                ))
            block.append(Spacer(1, 0.2 * cm))
            story.append(KeepTogether(block))

    # Recommendation
    rec = report.get("recommendation", "")
    if rec:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("Hiring Recommendation", h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
        story.append(Spacer(1, 0.2 * cm))
        rec_box = Table([[Paragraph(rec, body_style)]], colWidths=[17 * cm])
        rec_box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ede9fe")),
            ("BOX", (0, 0), (-1, -1), 1.5, PURPLE),
            ("PADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(rec_box)

    # Footer note
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Paragraph(
        f"Generated by KYS(Know Your Skills) | {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        "Powered by Groq Llama 3 + LangGraph",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.5,
                       textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)


def _generate_with_fpdf(report: dict, output_path: str):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "KYS(Know Your Skills) — Assessment Report", ln=True, align="C")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, f"Candidate: {report.get('candidate_name', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Role: {report.get('target_role', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Overall Score: {report.get('overall_score', 0)}/10", ln=True)
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Skill Scores", ln=True)
    pdf.set_font("Helvetica", size=10)
    for skill, data in report.get("skill_scores", {}).items():
        pdf.cell(0, 7, f"  {skill}: {data['score']}/10 — {data.get('evidence', '')[:80]}", ln=True)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Learning Plan", ln=True)
    pdf.set_font("Helvetica", size=10)
    for item in report.get("learning_plan", []):
        pdf.cell(0, 7, f"  {item['skill']} ({item.get('time_estimate', '')}) — {item.get('rationale', '')[:80]}", ln=True)

    pdf.output(output_path)


def _report_to_text(report: dict) -> str:
    lines = [
        "KYS(Know Your Skills) — ASSESSMENT REPORT",
        "=" * 50,
        f"Candidate: {report.get('candidate_name', 'N/A')}",
        f"Role: {report.get('target_role', 'N/A')}",
        f"Date: {report.get('date', 'N/A')}",
        f"Overall Score: {report.get('overall_score', 0)}/10",
        "",
        "SKILL SCORES",
        "-" * 30,
    ]
    for skill, data in report.get("skill_scores", {}).items():
        lines.append(f"  {skill}: {data['score']}/10")
        lines.append(f"    {data.get('evidence', '')}")

    lines += ["", "GAPS", "-" * 30]
    for gap in report.get("gaps", []):
        lines.append(f"  - {gap}")

    lines += ["", "LEARNING PLAN", "-" * 30]
    for item in report.get("learning_plan", []):
        lines.append(f"\n  {item['skill']} — {item.get('time_estimate', '')}")
        lines.append(f"  Why: {item.get('rationale', '')}")
        for r in item.get("resources", []):
            lines.append(f"    * {r.get('title', '')} ({r.get('url', '')})")

    lines += ["", "RECOMMENDATION", "-" * 30, report.get("recommendation", "")]
    return "\n".join(lines)
