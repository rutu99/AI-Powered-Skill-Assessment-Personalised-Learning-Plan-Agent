#  KYS(Know Your Skills) — Architecture & Scoring Logic

## System Architecture


<img width="944" height="970" alt="image" src="https://github.com/user-attachments/assets/e158dfd7-de9f-4dc4-8fa9-720914c10223" />


## Assessment State Machine

```
1. INIT
   └─► Parse JD + Resume via LLM
   └─► Extract: required_skills[], candidate_skills[], target_role

2. ASSESS_SKILL (per skill, looping)
   ├─► Ask Q1: Broad experience question
   ├─► Ask Q2: Deep-dive / follow-up
   └─► Ask Q3: Scenario / edge-case (high-importance skills only)

3. SCORE_SKILL (after each skill)
   └─► LLM evaluates all Q&A pairs for this skill
   └─► Returns: score (1-10), evidence, gap_detail

4. TRANSITION
   └─► Brief natural language bridge to next skill

5. REPORT GENERATION
   └─► Calculate overall_score (weighted average)
   └─► Identify gaps (score < 7)
   └─► Generate personalised learning plan via LLM
   └─► Produce hiring recommendation
```

## Scoring Logic

### Per-Skill Score (1–10)
The LLM evaluates the candidate's Q&A answers using this rubric:

|Score  | Meaning                                          |
| 1–3   | Little to no understanding; can't explain basics |
| 4–5   | Surface-level; has heard of it but can't apply   |
| 6–7   | Practical working knowledge; can use in projects |
| 8–9   | Strong; understands internals and edge cases     |
| 10    | Expert; can teach, architect, and innovate       |

### Overall Score
```
overall = mean(all skill scores)
```

### Gap Identification
Skills scoring **< 7** are flagged as gaps requiring development.

### Learning Plan Logic
For each gap:
1. LLM identifies **adjacent skills** — things close to what they already know
2. Generates **free resources** only (official docs, YouTube, freeCodeCamp, etc.)
3. Estimates **realistic time** based on existing proficiency
4. Prioritises by **job importance** (high-importance gaps first)

## Tech Stack


| LLM | Groq + llama-3.3-70b-versatile| Free tier, fast inference (300 tok/s) |
| Agent Framework | LangGraph + LangChain | State machine, structured prompting |
| UI | Gradio 4.x | HF Spaces native, fast prototyping |
| PDF | ReportLab | Professional output, free |
| PDF Parse | PyMuPDF | Fast, accurate |
| Storage | JSON files | Simple, portable, zero infra |
| Deployment | Hugging Face Spaces | Free hosting |

## Free Tools Only 
- Groq API — free tier (generous limits)
- Llama 3 70B — open-source Meta model
- LangGraph — open-source (MIT)
- LangChain — open-source (MIT)
- Gradio — open-source (Apache 2.0)
- ReportLab — open-source community edition
- PyMuPDF — open-source (AGPL)
- Hugging Face Spaces — free tier
