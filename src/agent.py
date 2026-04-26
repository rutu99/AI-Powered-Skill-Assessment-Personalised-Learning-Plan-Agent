"""
SkillAssessmentAgent — LangGraph-based conversational assessment engine.

Flow:
  INIT → EXTRACT_SKILLS → ASSESS_SKILL (loop) → SCORE → REPORT
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, TypedDict, Annotated

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# ─────────────────────────────────────────────────────
# LLM Initialisation (Groq — free tier, Llama 3 70B)
# ─────────────────────────────────────────────────────

def get_llm(temperature: float = 0.3):
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not set. "
            "Local: add it to your .env file. "
            "HF Spaces: add it as a Space Secret in Settings."
        )
    model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    max_tokens = int(os.environ.get("LLM_MAX_TOKENS", 1500))
    return ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=api_key,
        max_tokens=max_tokens,
    )


# ─────────────────────────────────────────────────────
# Agent State Schema
# ─────────────────────────────────────────────────────

class AgentState(TypedDict):
    jd_text: str
    resume_text: str
    candidate_name: str
    required_skills: list[dict]      # [{name, importance, category}]
    candidate_skills: list[str]      # skills from resume
    current_skill_idx: int
    current_question_count: int
    skill_scores: dict[str, dict]    # skill → {score, evidence, q_and_a}
    conversation_history: list[dict] # [{role, content}]
    phase: str                       # init|assessing|scoring|done
    target_role: str
    assessment_complete: bool


# ─────────────────────────────────────────────────────
# Prompts
# ─────────────────────────────────────────────────────

SKILL_EXTRACTION_PROMPT = """You are a senior technical recruiter.

Given this Job Description and Resume, extract:
1. Required skills from the JD (with importance: high/medium/low and category: technical/soft/domain)
2. Skills the candidate claims in their resume

Return ONLY valid JSON, no markdown fences:
{{
  "target_role": "<inferred job title>",
  "required_skills": [
    {{"name": "Python", "importance": "high", "category": "technical"}},
    ...
  ],
  "candidate_skills": ["Python", "SQL", ...]
}}

Job Description:
{jd_text}

Resume:
{resume_text}
"""

ASSESSMENT_QUESTION_PROMPT = """You are conducting a live technical interview.

Candidate: {candidate_name}
Current Skill Being Assessed: {skill_name} (importance: {importance})
Questions asked so far for this skill: {q_count}
Conversation so far:
{history}

Your goal: Assess the candidate's REAL proficiency in "{skill_name}".
- Ask ONE clear, specific question.
- For Q1: Start broad (e.g., "Can you explain how you've used X in a real project?")
- For Q2: Go deeper based on their answer (e.g., a follow-up or edge-case question)
- For Q3: Ask a scenario/problem-solving question

Do NOT repeat questions. Do NOT give the answer. Be conversational and professional.
Ask the question ONLY — no preamble like "Great!" or "Sure!".
"""

SKILL_SCORING_PROMPT = """You are a rigorous technical evaluator.

Skill: {skill_name}
Importance: {importance}
Candidate's Q&A for this skill:
{qa_text}

Score the candidate's proficiency in "{skill_name}" from 1–10:
- 1–3: Little to no real understanding
- 4–5: Surface-level, has heard of it
- 6–7: Practical working knowledge
- 8–9: Strong, can explain internals and edge cases
- 10: Expert, can teach it

Return ONLY valid JSON:
{{
  "score": <integer 1-10>,
  "evidence": "<one sentence explaining the score based on their answers>",
  "gap_detail": "<what they're missing, or 'None' if strong>"
}}
"""

LEARNING_PLAN_PROMPT = """You are a senior learning & development specialist.

Candidate: {candidate_name}
Target Role: {target_role}
Skill Gaps (score < 7):
{gaps_json}
Candidate's existing skills: {existing_skills}

Generate a personalised, realistic learning plan.
Focus on ADJACENT skills — things they can realistically learn given what they already know.
For each gap, provide 2–3 specific, free/open resources.

Return ONLY valid JSON:
{{
  "learning_plan": [
    {{
      "skill": "FastAPI",
      "priority": "high",
      "time_estimate": "2 weeks",
      "rationale": "They know Flask well, FastAPI is a natural step up",
      "resources": [
        {{
          "title": "FastAPI Official Tutorial",
          "url": "https://fastapi.tiangolo.com/tutorial/",
          "type": "Documentation",
          "duration": "8 hours"
        }},
        {{
          "title": "FastAPI Full Course – freeCodeCamp",
          "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA",
          "type": "Video",
          "duration": "6 hours"
        }}
      ]
    }}
  ],
  "recommendation": "<2-3 sentence hiring recommendation with overall assessment>"
}}
"""

TRANSITION_PROMPT = """You are conducting a skill assessment interview.

You just finished assessing: {prev_skill}
Score given: {score}/10
Next skill to assess: {next_skill}

Write a brief, natural 1-2 sentence transition to move to the next skill.
Be encouraging but honest. Don't inflate praise. Keep it professional.
"""

COMPLETION_PROMPT = """You are wrapping up a skill assessment interview.

Candidate: {candidate_name}
Skills assessed: {skills_summary}
Overall score: {overall_score}/10

Write a brief, warm closing message (2-3 sentences) thanking them and mentioning
that their full report with learning plan is being generated.
"""


# ─────────────────────────────────────────────────────
# Main Agent Class
# ─────────────────────────────────────────────────────

class SkillAssessmentAgent:
    def __init__(self):
        self.llm = get_llm()
        self.state: AgentState = self._empty_state()
        self._pending_skill_qa: list[dict] = []
        self._awaiting_answer: bool = False
        self._questions_for_current: list[str] = []

    def _empty_state(self) -> AgentState:
        return {
            "jd_text": "",
            "resume_text": "",
            "candidate_name": "",
            "required_skills": [],
            "candidate_skills": [],
            "current_skill_idx": 0,
            "current_question_count": 0,
            "skill_scores": {},
            "conversation_history": [],
            "phase": "init",
            "target_role": "",
            "assessment_complete": False,
        }

    # ── Public interface ──────────────────────────────

    def start(self, jd_text: str, resume_text: str, candidate_name: str) -> str:
        """Initialise state and return opening message."""
        self.state = self._empty_state()
        self.state["jd_text"] = jd_text
        self.state["resume_text"] = resume_text
        self.state["candidate_name"] = candidate_name

        # Extract skills via LLM
        extraction = self._extract_skills()
        self.state["required_skills"] = extraction.get("required_skills", [])
        self.state["candidate_skills"] = extraction.get("candidate_skills", [])
        self.state["target_role"] = extraction.get("target_role", "the role")
        self.state["phase"] = "assessing"

        # Build opening message
        skill_names = [s["name"] for s in self.state["required_skills"]]
        opening = (
            f"Hi {candidate_name}! 👋 I've reviewed the job description and your resume.\n\n"
            f"I'll be assessing your proficiency in **{len(skill_names)} key skill(s)**: "
            f"{', '.join(skill_names[:6])}{'...' if len(skill_names) > 6 else ''}.\n\n"
            #f"I'll ask 2–3 questions per skill. Please answer as you would in a real interview — "
            f"I'll ask 1–2 focused questions per skill. Please answer as you would in a real interview — "
            f"specific examples from your experience are highly valued.\n\n"
            f"Let's begin with: **{self.state['required_skills'][0]['name']}**\n\n"
        )

        # Ask first question
        first_question = self._ask_next_question()
        self._awaiting_answer = True
        return opening + first_question

    def respond(self, user_message: str) -> str:
        """Process user answer and advance the assessment state machine."""
        if self.state["phase"] != "assessing":
            return "The assessment is complete. Please generate your report."

        s = self.state
        current_skill = s["required_skills"][s["current_skill_idx"]]

        # Record the Q&A
        last_question = self._questions_for_current[-1] if self._questions_for_current else ""
        self._pending_skill_qa.append({"q": last_question, "a": user_message})
        s["current_question_count"] += 1
        s["conversation_history"].append({"role": "user", "content": user_message})

        
        total_skills = len(s["required_skills"])
        questions_per_skill = 2 if current_skill["importance"] == "high" else 1

        if s["current_question_count"] < questions_per_skill:
            # Ask another question for this skill
            next_q = self._ask_next_question()
            return next_q
        else:
            # Score this skill
            score_data = self._score_skill(current_skill, self._pending_skill_qa)
            s["skill_scores"][current_skill["name"]] = {
                "score": score_data["score"],
                "evidence": score_data["evidence"],
                "gap_detail": score_data["gap_detail"],
                "q_and_a": list(self._pending_skill_qa),
            }

            # Reset for next skill
            self._pending_skill_qa = []
            self._questions_for_current = []
            s["current_question_count"] = 0
            s["current_skill_idx"] += 1

            if s["current_skill_idx"] >= len(s["required_skills"]):
                # All done
                s["phase"] = "done"
                s["assessment_complete"] = True
                return self._closing_message()
            else:
                # Transition to next skill
                next_skill = s["required_skills"][s["current_skill_idx"]]
                transition = self._transition_message(
                    prev_skill=current_skill["name"],
                    score=score_data["score"],
                    next_skill=next_skill["name"],
                )
                next_q = self._ask_next_question()
                return transition + "\n\n" + next_q

    def is_ready_for_report(self) -> bool:
        return self.state.get("assessment_complete", False)

    def get_metadata(self) -> dict:
        return {
            "candidate_name": self.state["candidate_name"],
            "target_role": self.state["target_role"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    def generate_report(self) -> dict:
        s = self.state
        scores = s["skill_scores"]

        overall = round(
            sum(v["score"] for v in scores.values()) / max(len(scores), 1), 1
        )

        gaps = [
            {"skill": k, "score": v["score"], "gap_detail": v.get("gap_detail", "")}
            for k, v in scores.items()
            if v["score"] < 7
        ]

        learning_plan_data = self._generate_learning_plan(gaps)

        return {
            "candidate_name": s["candidate_name"],
            "target_role": s["target_role"],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "overall_score": overall,
            "skill_scores": scores,
            "gaps": [f"{g['skill']} (score: {g['score']}/10): {g['gap_detail']}" for g in gaps],
            "learning_plan": learning_plan_data.get("learning_plan", []),
            "recommendation": learning_plan_data.get("recommendation", ""),
        }

    # ── Private helpers ───────────────────────────────

    def _llm_json(self, prompt: str) -> dict:
        """Call LLM and parse JSON response robustly."""
        msgs = [SystemMessage(content="You are a precise AI that always returns valid JSON."),
                HumanMessage(content=prompt)]
        raw = self.llm.invoke(msgs).content.strip()
        # Strip markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Last resort: extract JSON object
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {}

    def _llm_text(self, prompt: str, temperature: float = 0.5) -> str:
        llm = get_llm(temperature=temperature)
        msgs = [HumanMessage(content=prompt)]
        return llm.invoke(msgs).content.strip()

    def _extract_skills(self) -> dict:
        prompt = SKILL_EXTRACTION_PROMPT.format(
            jd_text=self.state["jd_text"][:3000],
            resume_text=self.state["resume_text"][:3000],
        )
        result = self._llm_json(prompt)
        # Fallback
        if not result.get("required_skills"):
            result["required_skills"] = [{"name": "General Skills", "importance": "high", "category": "technical"}]
        importance_order = {"high": 0, "medium": 1, "low": 2}
        result["required_skills"] = sorted(result["required_skills"], key=lambda x: importance_order.get(x.get("importance", "low"), 2))[:5]   
        return result

    def _ask_next_question(self) -> str:
        s = self.state
        skill = s["required_skills"][s["current_skill_idx"]]
        history_text = self._format_history_for_prompt()

        prompt = ASSESSMENT_QUESTION_PROMPT.format(
            candidate_name=s["candidate_name"],
            skill_name=skill["name"],
            importance=skill["importance"],
            q_count=s["current_question_count"],
            history=history_text[-2000:] if history_text else "None yet.",
        )
        q = self._llm_text(prompt, temperature=0.4)
        self._questions_for_current.append(q)
        s["conversation_history"].append({"role": "assistant", "content": q})
        return q

    def _score_skill(self, skill: dict, qa_pairs: list[dict]) -> dict:
        qa_text = "\n".join([f"Q: {p['q']}\nA: {p['a']}" for p in qa_pairs])
        prompt = SKILL_SCORING_PROMPT.format(
            skill_name=skill["name"],
            importance=skill["importance"],
            qa_text=qa_text,
        )
        result = self._llm_json(prompt)
        if "score" not in result:
            result = {"score": 5, "evidence": "Unable to score.", "gap_detail": "Unknown"}
        result["score"] = max(1, min(10, int(result["score"])))
        return result

    def _transition_message(self, prev_skill: str, score: int, next_skill: str) -> str:
        prompt = TRANSITION_PROMPT.format(
            prev_skill=prev_skill, score=score, next_skill=next_skill
        )
        return self._llm_text(prompt, temperature=0.6)

    def _closing_message(self) -> str:
        s = self.state
        scores = s["skill_scores"]
        overall = round(sum(v["score"] for v in scores.values()) / max(len(scores), 1), 1)
        summary = ", ".join([f"{k}: {v['score']}/10" for k, v in scores.items()])
        prompt = COMPLETION_PROMPT.format(
            candidate_name=s["candidate_name"],
            skills_summary=summary,
            overall_score=overall,
        )
        closing = self._llm_text(prompt, temperature=0.5)
        return (
            closing
            + "\n\n✅ **Assessment complete!** Click **Generate Full Report & Learning Plan** above."
        )

    def _generate_learning_plan(self, gaps: list[dict]) -> dict:
        if not gaps:
            return {
                "learning_plan": [],
                "recommendation": f"{self.state['candidate_name']} demonstrates strong proficiency across all assessed skills and appears well-suited for {self.state['target_role']}."
            }
        prompt = LEARNING_PLAN_PROMPT.format(
            candidate_name=self.state["candidate_name"],
            target_role=self.state["target_role"],
            gaps_json=json.dumps(gaps, indent=2),
            existing_skills=", ".join(self.state["candidate_skills"][:15]),
        )
        return self._llm_json(prompt)

    def _format_history_for_prompt(self) -> str:
        history = self.state["conversation_history"][-10:]  # last 10 turns
        lines = []
        for msg in history:
            role = "Interviewer" if msg["role"] == "assistant" else "Candidate"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
