# KYS(Know Your Skills)-AI — Skill Assessment & Personalised Learning Plan Agent
This is a conversational AI agent that takes a Job Description and a candidate's resume, assess them in real-time to assess actual proficiency on each required skill, identifies gaps, and generates a personalised learning plan with curated free resources and time estimates.



KYS(Know Your Skills)-AI is a conversational AI agent that takes a Job Description and a candidate's resume, **interviews them in real-time** to assess actual proficiency on each required skill, identifies gaps, and generates a **personalised learning plan** with curated free resources and time estimates.

---

##  Live Demo

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/rutuk2/SkillSense-26)

**Demo Video:** [loom::https://www.loom.com/share/7b98a4ffab634075ab9f7c892c9e2ef3](#) *(3–5 min walkthrough)*

---

##  Features

- 🎯 **Conversational Assessment** — Real LLM-driven Q&A, 2–3 questions per skill
- 📊 **Skill Scoring** — Each skill scored 1–10 with evidence from answers
- 🗺 **Learning Plan** — Personalised plan focused on adjacent skills, with free resources
- 📄 **PDF Export** — Professional formatted report downloadable as PDF
- 💾 **Assessment History** — All past assessments saved and viewable
- 🎭 **Role Templates** — Pre-built JDs for 7 common roles
- 📈 **Gap Analysis** — Identifies exact weaknesses with specificity

---

## 🏗 Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full architecture diagram and scoring logic.

**TL;DR:**
```
JD + Resume → Skill Extraction (LLM) → Conversational Q&A Loop → 
Per-Skill Scoring (LLM) → Gap Analysis → Learning Plan Generation (LLM) → PDF Report
```

**Stack:**
- **LLM:** Groq API + Llama 3 70B (free tier)
- **Agent Framework:** LangGraph + LangChain
- **UI:** Gradio 4.x on Hugging Face Spaces
- **PDF:** ReportLab
- **Storage:** JSON file persistence

---

## 🛠 Local Setup

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com) (takes ~1 min to get)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/skillsense-ai
cd skillsense-ai
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

Or export directly:
```bash
export GROQ_API_KEY="your_key_here"
```

### Run

```bash
python app.py
# Open http://localhost:7860
```

---

## 🤗 Hugging Face Spaces Deployment

1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
   - SDK: **Gradio**
   - Hardware: **CPU Basic** (free)

2. Push this repo to the Space:
```bash
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/skillsense-ai
git push space main
```

3. Add your `GROQ_API_KEY` as a **Space Secret**:
   - Settings → Variables and Secrets → New Secret
   - Name: `GROQ_API_KEY`
   - Value: `gsk_...`

---

## 📁 Project Structure

```
skillsense-ai/
├── app.py                     # Main Gradio app + UI
├── src/
│   ├── agent.py               # Core LangGraph assessment agent
│   ├── resume_parser.py       # PDF/text resume extraction
│   ├── report_generator.py    # PDF report generation (ReportLab)
│   ├── storage.py             # JSON-based assessment persistence
│   └── role_templates.py      # Pre-built JD templates
├── ARCHITECTURE.md            # System design + scoring logic
├── requirements.txt
├── .env
└── README.md
```

---

## 📋 Sample Inputs & Outputs

### Sample Input: Job Description
```
Position: Data Analyst
Required: SQL (complex queries), Python (Pandas), Tableau, 
A/B testing, Statistical analysis, BigQuery
```

### Sample Input: Resume Snippet
```
Sayali Kamble | Data Analyst | 2 years experience
Skills: Python, SQL, Excel, Power BI
Projects: Sales dashboard in Power BI, customer churn analysis in Python
```

### Sample Assessment Flow
```
Agent: Hi Sayali ! I'll be assessing: SQL, Python, Tableau, A/B Testing, BigQuery.
       Let's begin with SQL.
       Can you describe a complex SQL query you've written — what problem did it solve?

Sayali: I wrote a multi-join query to aggregate sales data across 5 tables, 
       including CTEs to stage intermediate results...

Agent: Good. Can you explain when you'd use a window function vs GROUP BY?

Sayali: Window functions are for row-level calculations without collapsing rows...

Agent: Final SQL question: You have a 50M row table that's slow on a date filter. 
       How would you diagnose and fix this?

Sayali: I'd check if there's an index on the date column, run EXPLAIN ANALYZE...

[Agent internally scores SQL: 8/10]

Agent: Good work on SQL. Moving to Python...
```

### Sample Report Output
```
SKILL SCORES:
  SQL:          8/10 — Strong understanding of CTEs, window functions, indexing
  Python:       7/10 — Solid Pandas/NumPy, some gaps in advanced optimisation  
  Tableau:      4/10 — Limited exposure; mostly Power BI experience
  A/B Testing:  5/10 — Knows the concept but uncertain on statistical significance
  BigQuery:     3/10 — No direct experience, some SQL transferable

OVERALL SCORE: 5.4/10

GAPS: Tableau, A/B Testing, BigQuery

LEARNING PLAN:
  Tableau (2 weeks, High Priority)
  - Tableau Public Free Training: https://www.tableau.com/learn/training
  - YouTube: Tableau Full Course (6h) — freeCodeCamp
  
  A/B Testing (1 week)
  - Khan Academy: Statistics & Probability
  - Udacity: A/B Testing Free Course
  
  BigQuery (1 week)
  - Google Cloud Skills Boost: BigQuery free tier labs

RECOMMENDATION: Sayali shows genuine strength in SQL and Python, which are 
the hardest skills to teach. The gaps in Tableau and BigQuery are learnable 
in 3–4 weeks given her SQL foundation. Recommend conditional offer with 
30-day learning targets.
```

---

##  Models Used

 Skill extraction | llama-3.3-70b-versatile (Groq) | Accurate JSON structured extraction |
 Question generation | llama-3.3-70b-versatile (Groq) | Natural, contextual interview questions |
 Skill scoring | llama-3.3-70b-versatile (Groq) | Nuanced evaluation with evidence |
 Learning plan | llama-3.3-70b-versatile (Groq) | Realistic, adjacent skill recommendations |

All models via **Groq free tier** — no cost.

---

##  Scoring System


| 1–3 | Beginner | Little real understanding |
| 4–5 | Aware | Surface-level, can't apply |
| 6–7 | Proficient | Working knowledge |
| 8–9 | Advanced | Deep understanding |
| 10 | Expert | Can architect and teach |

**Gap threshold:** Score < 7 triggers learning plan item.


## 🤝 Contributing

PRs welcome! Key areas for contribution:
- Additional role templates
- SQLite-based persistent storage
- Candidate improvement tracking over time
- Interview export formats (JSON, CSV)

---

## 📄 License

MIT License — free to use, modify, deploy.

---

*Built with ❤️ using Groq + Llama  + LangGraph + Gradio* built for Catalyst Hackathon by Deccan.ai
