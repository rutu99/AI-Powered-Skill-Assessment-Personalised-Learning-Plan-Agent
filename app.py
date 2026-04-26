"""
SkillSense AI — app.py
Gradio 6.x, session-only storage (no login, no persistence).
Page refresh clears everything.
"""

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
import os
import tempfile
import uuid

from src.agent import SkillAssessmentAgent
from src.resume_parser import extract_text_from_pdf
from src.report_generator import generate_pdf_report
from src.storage import AssessmentStorage
from src.role_templates import ROLE_TEMPLATES

# ── In-memory storage (lives only while server is running) ────
storage = AssessmentStorage()

# ── Per-session agent registry ────────────────────────────────
_agents: dict[str, SkillAssessmentAgent] = {}

def get_agent(session_id: str) -> SkillAssessmentAgent:
    if session_id not in _agents:
        _agents[session_id] = SkillAssessmentAgent()
    return _agents[session_id]


# ─────────────────────────────────────────────────────────────
# Message helpers
# ─────────────────────────────────────────────────────────────

def bot_msg(text: str) -> dict:
    return {"role": "assistant", "content": text}

def user_msg(text: str) -> dict:
    return {"role": "user", "content": text}


# ─────────────────────────────────────────────────────────────
# Tab 1 — Assessment
# ─────────────────────────────────────────────────────────────

def load_role_template(role: str) -> str:
    return ROLE_TEMPLATES.get(role, "")


def clear_session(session_id: str):
    if session_id and session_id in _agents:
        del _agents[session_id]
    return (
        [],           # chatbot
        "",           # session_id_state
        "",           # candidate_name
        "(Custom)",   # role_template
        "",           # jd_input
        None,         # resume_file
        "",           # resume_text
        "",           # report_display
        None,         # pdf_download
        gr.update(interactive=False),  # msg_input
    )


def start_assessment(
    session_id: str,
    jd_text: str,
    resume_file,
    resume_text_input: str,
    candidate_name: str,
    history: list,
):
    if not jd_text.strip():
        return (
            history + [bot_msg("⚠️ Please provide a Job Description.")],
            session_id, gr.update(),
        )

    resume_raw = ""
    if resume_file is not None:
        resume_raw = extract_text_from_pdf(resume_file)
    elif resume_text_input.strip():
        resume_raw = resume_text_input.strip()

    if not resume_raw:
        return (
            history + [bot_msg("⚠️ Please upload a resume PDF or paste resume text.")],
            session_id, gr.update(),
        )

    if not session_id:
        session_id = str(uuid.uuid4())

    agent = get_agent(session_id)
    opening = agent.start(
        jd_text=jd_text,
        resume_text=resume_raw,
        candidate_name=candidate_name or "Candidate",
    )
    return (
        history + [bot_msg(opening)],
        session_id,
        gr.update(interactive=True),
    )


def chat(user_message: str, history: list, session_id: str):
    if not session_id or not user_message.strip():
        return history, "", session_id
    agent = get_agent(session_id)
    response = agent.respond(user_message)
    return history + [user_msg(user_message), bot_msg(response)], "", session_id


def generate_report(session_id: str, history: list):
    if not session_id:
        return "⚠️ No active assessment session.", None, None

    agent = get_agent(session_id)
    if not agent.is_ready_for_report():
        return (
            "⚠️ Assessment still in progress. Continue until all skills are evaluated.",
            None, None,
        )

    report    = agent.generate_report()
    record_id = storage.save(session_id, agent.get_metadata(), report)
    pdf_path  = generate_pdf_report(report, record_id)
    return format_report_md(report), pdf_path, record_id


def format_report_md(report: dict) -> str:
    lines = []
    lines.append(f"# 📊 Assessment Report: {report['candidate_name']}")
    lines.append(f"**Role:** {report['target_role']}  |  **Date:** {report['date']}")
    lines.append(f"**Overall Score:** {report['overall_score']}/10\n")

    lines.append("## 🎯 Skill Scores")
    for skill, data in report["skill_scores"].items():
        score = int(data["score"])
        bar = "█" * score + "░" * (10 - score)
        lines.append(f"- **{skill}**: `{bar}` {score}/10")
        if data.get("evidence"):
            lines.append(f"  *{data['evidence']}*")

    lines.append("\n## 🔴 Identified Gaps")
    for gap in report.get("gaps", []):
        lines.append(f"- {gap}")

    lines.append("\n## 📚 Personalised Learning Plan")
    for item in report.get("learning_plan", []):
        lines.append(f"\n### {item['skill']} *(Est. {item['time_estimate']})*")
        lines.append(f"**Why:** {item['rationale']}")
        lines.append("**Resources:**")
        for r in item.get("resources", []):
            lines.append(f"  - [{r['title']}]({r['url']}) — *{r['type']}*")

    lines.append("\n## 💡 Hiring Recommendation")
    lines.append(report.get("recommendation", ""))
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Tab 2 — Session History
# ─────────────────────────────────────────────────────────────

def load_history():
    records = storage.list_all()
    if not records:
        return "No assessments this session yet.", gr.update(choices=[])
    choices = [
        f"{r['date']} | {r['candidate_name']} | {r['target_role']} | Score: {r['overall_score']}/10"
        for r in records
    ]
    return f"Found **{len(records)}** assessment(s) this session.", gr.update(choices=choices)


def view_past_record(selection: str):
    if not selection:
        return "Select a record above."
    for r in storage.list_all():
        label = f"{r['date']} | {r['candidate_name']} | {r['target_role']} | Score: {r['overall_score']}/10"
        if label == selection:
            report = storage.load(r["id"])
            return format_report_md(report) if report else "Report not found."
    return "Record not found."


def download_past_pdf(selection: str):
    if not selection:
        return None
    for r in storage.list_all():
        label = f"{r['date']} | {r['candidate_name']} | {r['target_role']} | Score: {r['overall_score']}/10"
        if label == selection:
            report = storage.load(r["id"])
            return generate_pdf_report(report, r["id"]) if report else None
    return None


# ─────────────────────────────────────────────────────────────
# CSS & Theme
# ─────────────────────────────────────────────────────────────

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

body, .gradio-container { font-family: 'Space Grotesk', sans-serif !important; background: #0d0d14 !important; }
.app-header { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 40%, #06b6d4 100%); border-radius: 16px; padding: 28px 32px 22px; margin-bottom: 8px; box-shadow: 0 8px 32px rgba(79,70,229,0.35); }
.app-header h1 { font-family: 'DM Mono', monospace !important; font-size: 2rem !important; color: #fff !important; margin: 0 !important; }
.app-header p { color: rgba(255,255,255,0.82) !important; font-size: 0.95rem !important; margin: 6px 0 0 !important; }
.tabs > .tab-nav { background: #13131f !important; border-bottom: 1px solid #1e1e30 !important; }
.tabs > .tab-nav button { color: #6b7280 !important; font-weight: 600 !important; padding: 12px 20px !important; border-bottom: 2px solid transparent !important; }
.tabs > .tab-nav button.selected { color: #a78bfa !important; border-bottom: 2px solid #7c3aed !important; }
.gr-box, .gr-form, .gradio-group, .block { background: #13131f !important; border: 1px solid #1e1e30 !important; border-radius: 12px !important; }
input, textarea { background: #0d0d14 !important; border: 1px solid #2d2d45 !important; color: #e2e8f0 !important; border-radius: 8px !important; }
input:focus, textarea:focus { border-color: #7c3aed !important; box-shadow: 0 0 0 3px rgba(124,58,237,0.18) !important; }
label span { color: #94a3b8 !important; font-size: 0.8rem !important; font-weight: 600 !important; letter-spacing: 0.05em !important; text-transform: uppercase !important; }
button[variant="primary"] { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; border: none !important; color: #fff !important; font-weight: 700 !important; border-radius: 10px !important; box-shadow: 0 4px 14px rgba(124,58,237,0.3) !important; }
button[variant="secondary"] { background: #1e1e30 !important; border: 1px solid #2d2d45 !important; color: #a78bfa !important; font-weight: 600 !important; border-radius: 10px !important; }
.clear-btn button { background: linear-gradient(135deg, #d97706, #f59e0b) !important; border: none !important; color: #fff !important; font-weight: 700 !important; border-radius: 10px !important; }
.chatbot { background: #0d0d14 !important; border: 1px solid #1e1e30 !important; border-radius: 12px !important; }
.chatbot .message.user div { background: linear-gradient(135deg, #4f46e5, #7c3aed) !important; color: #fff !important; border-radius: 12px 12px 2px 12px !important; }
.chatbot .message.bot div { background: #1a1a2e !important; border: 1px solid #2d2d45 !important; color: #e2e8f0 !important; border-radius: 12px 12px 12px 2px !important; }
footer { display: none !important; }
"""

THEME = gr.themes.Base(
    primary_hue="violet",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Space Grotesk"), "sans-serif"],
)


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────

def build_app():
    with gr.Blocks(title="SkillSense AI") as demo:

        session_id_state = gr.State("")

        gr.HTML("""
        <div class="app-header">
            <h1>🧠 SkillSense AI</h1>
            <p>Conversational skill assessment &amp; personalised learning plan generator &nbsp;·&nbsp;
               Groq × Llama 3.3 × LangGraph &nbsp;·&nbsp; Free &amp; Open Source</p>
        </div>
        """)

        with gr.Tabs():

            # ── TAB 1: Assessment ──────────────────────────────
            with gr.Tab("🎯 Assessment"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📋 Setup")
                        candidate_name = gr.Textbox(label="Candidate Name", placeholder="e.g. Priya Sharma")
                        role_template  = gr.Dropdown(
                            choices=["(Custom)"] + list(ROLE_TEMPLATES.keys()),
                            label="Role Template", value="(Custom)",
                        )
                        jd_input    = gr.Textbox(label="Job Description", placeholder="Paste JD or pick a template above...", lines=9)
                        resume_file = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"], type="filepath")
                        resume_text = gr.Textbox(label="Or Paste Resume Text", placeholder="Paste plain-text resume...", lines=6)
                        with gr.Row():
                            start_btn = gr.Button("🚀 Start", variant="primary", scale=3)
                            clear_btn = gr.Button("🗑 Clear", variant="secondary", scale=1, elem_classes=["clear-btn"])

                    with gr.Column(scale=2):
                        gr.Markdown("### 💬 Live Assessment")
                        chatbot = gr.Chatbot(label="", height=460)
                        with gr.Row():
                            msg_input = gr.Textbox(label="", placeholder="Type your answer and press Enter...", scale=5, interactive=False)
                            send_btn  = gr.Button("Send ▶", scale=1, variant="primary")

                gr.Markdown("---")
                report_btn = gr.Button("📊 Generate Full Report & Learning Plan", variant="primary")
                with gr.Row():
                    with gr.Column(scale=3):
                        report_display = gr.Markdown()
                    with gr.Column(scale=1, min_width=180):
                        pdf_download = gr.File(label="⬇ Download PDF")

                role_template.change(load_role_template, inputs=role_template, outputs=jd_input)
                start_btn.click(
                    start_assessment,
                    inputs=[session_id_state, jd_input, resume_file, resume_text, candidate_name, chatbot],
                    outputs=[chatbot, session_id_state, msg_input],
                )
                send_btn.click(chat, inputs=[msg_input, chatbot, session_id_state], outputs=[chatbot, msg_input, session_id_state])
                msg_input.submit(chat, inputs=[msg_input, chatbot, session_id_state], outputs=[chatbot, msg_input, session_id_state])
                report_btn.click(generate_report, inputs=[session_id_state, chatbot], outputs=[report_display, pdf_download, gr.State()])
                clear_btn.click(
                    clear_session,
                    inputs=[session_id_state],
                    outputs=[chatbot, session_id_state, candidate_name, role_template,
                             jd_input, resume_file, resume_text, report_display, pdf_download, msg_input],
                )

            # ── TAB 2: Session History ─────────────────────────
            with gr.Tab("📁 This Session"):
                gr.Markdown("### 🗂 Assessments This Session")
                gr.HTML("<p style='color:#6b7280;font-size:0.85rem;margin-top:-8px;'>Cleared automatically when the page is refreshed.</p>")

                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                    hist_status = gr.Markdown("")

                hist_list = gr.Radio(label="", choices=[], interactive=True)
                with gr.Row():
                    view_btn = gr.Button("👁 View Report", variant="primary")
                    dl_btn   = gr.Button("⬇ Download PDF", variant="secondary")

                past_report_display = gr.Markdown()
                past_pdf_download   = gr.File(label="PDF")

                refresh_btn.click(load_history, outputs=[hist_status, hist_list])
                view_btn.click(view_past_record, inputs=hist_list, outputs=past_report_display)
                dl_btn.click(download_past_pdf, inputs=hist_list, outputs=past_pdf_download)

        gr.HTML("""
        <div style="text-align:center;padding:16px 0 8px;color:#4b5563;font-size:0.78rem;border-top:1px solid #1e1e30;margin-top:12px;">
            SkillSense AI &nbsp;·&nbsp; Groq (Llama 3.3-70B) + LangGraph + Gradio &nbsp;·&nbsp; Free &amp; Open Source
        </div>
        """)

    return demo


if __name__ == "__main__":
    _host = os.environ.get("SERVER_NAME", "127.0.0.1")
    _port = int(os.environ.get("SERVER_PORT", 7860))
    _key  = os.environ.get("GROQ_API_KEY", "")

    print()
    print("=" * 55)
    print(" SkillSense AI — Starting")
    print("=" * 55)
    if not _key:
        print(" WARNING: GROQ_API_KEY not set! Add it to .env")
    print(f" Open in browser: http://{_host}:{_port}")
    print("=" * 55)
    print()

    app     = build_app()
    _pdf_dir = os.path.join(tempfile.gettempdir(), "skillsense_reports")
    os.makedirs(_pdf_dir, exist_ok=True)

    app.launch(
        server_name=_host,
        server_port=_port,
        share=os.environ.get("GRADIO_SHARE", "false").lower() == "true",
        allowed_paths=[_pdf_dir],
        theme=THEME,
        css=CSS,
    )