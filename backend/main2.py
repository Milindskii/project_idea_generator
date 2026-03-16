"""
main.py — Entry point for the Full Pipeline (Trend Analysis + Idea Generation + Ranking)

Run:
    python main.py

Prerequisites:
    pip install pydantic requests scikit-learn numpy
    ollama pull nomic-embed-text
    ollama pull mistral
    ollama serve
"""

import json
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))
# Also add agent1_research to path so it can import its own tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agent1_research"))

from trend_analysis import TrendAnalysisAgent, ResearchData, Paper, Repo
from pipeline.idea_pipeline import IdeaPipeline
from agent1_research.research_agent import research_agent

# ---------------------------------------------------------------------------
# Run Complete Flow
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("   AI System End-to-End Pipeline: Research Data -> Ranked Ideas")
    print("=" * 70)

    # 0. User Query & Research Agent
    query = "compliance review system"
    print(f"\n>>> PHASE 0: Research Agent (Query: '{query}')")
    
    # Call the real research agent
    result = research_agent(query)
    
    if not result:
        print("[ERROR] Research agent failed to produce valid output.")
        return
        
    structured, raw_papers, raw_repos = result

    # Convert agent 1 output to ResearchData format directly from the raw APIs
    research_data = ResearchData(
        papers=[
            Paper(
                title=p.get('paper_title', p.get('title', 'Unknown Title')),
                abstract=p.get('content', p.get('abstract', p.get('summary', ''))),
                keywords=[],
                year=2024
            )
            for p in raw_papers
        ],
        repos=[
            Repo(
                name=r.get('name', r.get('repo', 'Unknown Repo')),
                description=r.get('description', ''),
                tags=[],
                stars=r.get('stars', 0)
            )
            for r in raw_repos
        ]
    )

    # 1. Run Trend Analysis
    print("\n>>> PHASE 1: Trend Analysis Agent")
    trend_agent = TrendAnalysisAgent(
        ollama_model="mistral",
        ollama_base_url="http://localhost:11434",
        velocity_threshold=0.5,
        top_k_trending=8,
        current_year=2024,
    )
    
    # Run the Trend Analysis on the gathered Research Data
    trend_output = trend_agent.run(research_data)
    trend_dict = trend_output.model_dump()

    print("\n   [Extracted Trends Summary]")
    print(f"   Trending Topics: {', '.join(trend_dict['trending_topics'][:5])}")
    print(f"   Emerging Topics: {', '.join(trend_dict['emerging_topics'][:5])}")
    print(f"   Found {len(trend_dict['topic_clusters'])} topic clusters.")

    # 2. Run Idea Generation & Ranking
    print("\n>>> PHASE 2: Idea Pipeline (Generation + Ranking)")
    idea_pipeline = IdeaPipeline(
        ollama_model="mistral",
        ollama_base_url="http://localhost:11434",
        n_ideas=5,       # Generate 5 raw ideas
        top_k=3,         # Return top 3 ranked
        use_llm_scoring=True,
    )

    # User Context from the user's prompt requirement
    user_context = "The builder is an intermediate-level developer trying to create a compliance review system by his own. Ideas must be tailored for this skill level and specific use case."

    # Pass the output of Trend Analysis into the Idea Pipeline
    result = idea_pipeline.run(trend_dict, user_context=user_context)

    # 3. Pretty Print Final Results
    print("\n" + "=" * 70)
    print("   FINAL OUTPUT: TOP RANKED AI IDEAS")
    print("=" * 70)
    for ranked in result.ranked_ideas:
        print(f"\nRank #{ranked.rank} — {ranked.idea_title}")
        print(f"  Final Score : {ranked.final_score}/10")
        print(f"  Novelty     : {ranked.novelty_score}/10")
        print(f"  Impact      : {ranked.impact_score}/10")
        print(f"  Feasibility : {ranked.feasibility_score}/10")
        print(f"  Complexity  : {ranked.complexity_score}/10")
        print(f"  Justification: {ranked.justification}")

    print("\n" + "=" * 70)
    print("   END OF PIPELINE")
    print("=" * 70)


if __name__ == "__main__":
    main()
