"""
pipeline/idea_pipeline.py

Orchestrates the full Idea Generation + Ranking pipeline.

Usage:
    from pipeline.idea_pipeline import IdeaPipeline
    result = IdeaPipeline().run(trend_report_dict)
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.idea_schema import TrendReport, IdeaPipelineOutput
from agents.idea_generator import IdeaGeneratorAgent
from agents.idea_ranker import IdeaRankerAgent


class IdeaPipeline:
    """
    End-to-end idea generation and ranking pipeline.

    Args:
        ollama_model:    Ollama model to use (default: llama3).
        ollama_base_url: Ollama API base URL.
        n_ideas:         Number of ideas to generate before ranking.
        top_k:           Number of top ideas to return after ranking.
        use_llm_scoring: Whether to use LLM to enrich impact scores.
    """

    def __init__(
        self,
        ollama_model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        n_ideas: int = 5,
        top_k: int = 3,
        use_llm_scoring: bool = True,
    ):
        self.generator = IdeaGeneratorAgent(
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url,
            n_ideas=n_ideas,
        )
        self.ranker = IdeaRankerAgent(
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url,
            top_k=top_k,
            use_llm_scoring=use_llm_scoring,
        )

    def run(self, trend_report: dict | TrendReport, user_context: str = "") -> IdeaPipelineOutput:
        """
        Run the full pipeline.

        Returns:
            IdeaPipelineOutput with all generated ideas + top-ranked ideas.
        """
        print("\n[Step 1/2] Generating ideas from trend insights \u2026")
        ideas = self.generator.run(trend_report, user_context=user_context)
        print(f"           ✓ Generated {len(ideas)} idea(s).")

        print("[Step 2/2] Ranking ideas by Novelty, Impact, Feasibility …")
        ranked = self.ranker.run(ideas)
        print(f"           ✓ Ranked top {len(ranked)} idea(s).")

        return IdeaPipelineOutput(
            generated_ideas=ideas,
            ranked_ideas=ranked,
        )
