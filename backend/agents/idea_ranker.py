"""
agents/idea_ranker.py

Idea Ranking Agent — evaluates and ranks generated AI project ideas.

Scoring formula:
  Final Score = 0.4 * Novelty + 0.3 * Impact + 0.2 * Feasibility - 0.1 * Complexity

All scores are on a 0–10 scale. Top 3 ideas are returned.
"""

from __future__ import annotations

import json
import re
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.idea_schema import ProjectIdea, RankedIdea

# ---------------------------------------------------------------------------
# Score mapping helpers
# ---------------------------------------------------------------------------

_LABEL_TO_SCORE = {"Low": 3.0, "Medium": 6.5, "High": 9.0}
_DIFFICULTY_TO_COMPLEXITY = {"Beginner": 2.0, "Medium": 5.5, "Advanced": 8.5}


def _label_score(label: str) -> float:
    return _LABEL_TO_SCORE.get(label, 5.0)


def _difficulty_to_complexity(level: str) -> float:
    return _DIFFICULTY_TO_COMPLEXITY.get(level, 5.5)


# ---------------------------------------------------------------------------
# LLM-powered scorer (optional enrichment)
# ---------------------------------------------------------------------------

_RANKER_SYSTEM_PROMPT = """You are an expert AI project evaluator.

Score each AI project idea on a 0–10 scale for:
- impact_score: How useful and impactful would this system be for real users?
- justification: One sentence explaining the scores.

Return ONLY valid JSON (no markdown, no extra text):
{
  "scores": [
    {
      "idea_title": "string",
      "impact_score": float,
      "justification": "string"
    }
  ]
}"""


def _call_ollama_ranker(
    ideas: list[ProjectIdea],
    model: str,
    base_url: str,
) -> dict | None:
    """Ask the LLM to assign impact scores. Returns parsed dict or None."""
    summaries = [
        {"idea_title": idea.idea_title, "solution": idea.solution, "technologies_used": idea.technologies_used}
        for idea in ideas
    ]
    user_prompt = f"Score these AI project ideas:\n{json.dumps(summaries, indent=2)}"

    try:
        import requests
        resp = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _RANKER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2, "num_predict": 1024},
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception as exc:
        print(f"[WARN] Ranker LLM call failed: {exc}")
    return None


# ---------------------------------------------------------------------------
# Deterministic scoring (always runs — LLM enriches impact only)
# ---------------------------------------------------------------------------

def _compute_final_score(novelty: float, impact: float, feasibility: float, complexity: float) -> float:
    """Final Score = 0.4*N + 0.3*I + 0.2*F - 0.1*C  (capped 0–10)"""
    score = 0.4 * novelty + 0.3 * impact + 0.2 * feasibility - 0.1 * complexity
    return round(max(0.0, min(10.0, score)), 2)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class IdeaRankerAgent:
    """
    Scores and ranks a list of ProjectIdea objects.
    Uses deterministic scoring for Novelty, Feasibility, and Complexity.
    Optionally uses Ollama LLM to enrich Impact scores.
    Returns top-k RankedIdea objects.
    """

    def __init__(
        self,
        ollama_model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        top_k: int = 3,
        use_llm_scoring: bool = True,
    ):
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.top_k = top_k
        self.use_llm_scoring = use_llm_scoring

    def run(self, ideas: list[ProjectIdea]) -> list[RankedIdea]:
        if not ideas:
            return []

        # Try LLM impact scoring
        llm_impact_map: dict[str, tuple[float, str]] = {}
        if self.use_llm_scoring:
            llm_result = _call_ollama_ranker(ideas, self.ollama_model, self.ollama_base_url)
            if llm_result and "scores" in llm_result:
                for entry in llm_result["scores"]:
                    title = entry.get("idea_title", "")
                    impact = float(entry.get("impact_score", 6.0))
                    justification = entry.get("justification", "")
                    llm_impact_map[title] = (max(0, min(10, impact)), justification)

        # Build RankedIdea for each idea
        scored: list[RankedIdea] = []
        for idea in ideas:
            novelty = _label_score(idea.novelty_score)
            feasibility = _label_score(idea.feasibility_score)
            complexity = _difficulty_to_complexity(idea.difficulty_level)

            # Use LLM impact if available, else deterministic estimate
            if idea.idea_title in llm_impact_map:
                impact, justification = llm_impact_map[idea.idea_title]
            else:
                # Deterministic estimate: average novelty + feasibility as proxy
                impact = round((novelty + feasibility) / 2, 1)
                justification = (
                    f"Assessed as {idea.novelty_score.lower()} novelty and "
                    f"{idea.feasibility_score.lower()} feasibility; "
                    f"targeting {', '.join(idea.target_users)}."
                )

            final = _compute_final_score(novelty, impact, feasibility, complexity)
            scored.append(
                RankedIdea(
                    idea_title=idea.idea_title,
                    novelty_score=novelty,
                    feasibility_score=feasibility,
                    impact_score=impact,
                    complexity_score=complexity,
                    final_score=final,
                    rank=0,  # assigned after sorting
                    justification=justification,
                )
            )

        # Sort descending and assign ranks
        scored.sort(key=lambda x: x.final_score, reverse=True)
        for i, item in enumerate(scored):
            item.rank = i + 1

        return scored[: self.top_k]
