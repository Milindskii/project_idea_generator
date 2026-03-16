"""
Idea Generating Agent
Part of the Multi-Agent AI Project Idea Generator

Pipeline Position:
  Research Agent → Trend Analysis Agent → Idea Generating Agent (THIS) → Evaluation Agent

Input:  TrendAnalysisOutput (structured JSON from Trend Analysis Agent)
Output: GeneratedIdeasOutput (structured JSON with novel AI project ideas)
"""

from __future__ import annotations

import json
import re
import random
from itertools import combinations
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Data Models — Input (mirrors TrendAnalysisOutput from trend_analysis.py)
# ---------------------------------------------------------------------------

class TopicCluster(BaseModel):
    cluster_name: str
    papers: list[str]


class TrendAnalysisOutput(BaseModel):
    trending_topics: list[str] = Field(default_factory=list)
    emerging_topics: list[str] = Field(default_factory=list)
    research_gaps: list[str] = Field(default_factory=list)
    topic_clusters: list[TopicCluster] = Field(default_factory=list)
    suggested_combinations: list[list[str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Data Models — Output
# ---------------------------------------------------------------------------

class ProjectIdea(BaseModel):
    idea_title: str = Field(description="Short, catchy title for the AI project.")
    problem_statement: str = Field(description="The real-world problem this project solves.")
    solution: str = Field(description="How the project addresses the problem using modern AI.")
    technologies_used: list[str] = Field(description="Specific AI/ML technologies and tools involved.")
    implementation_outline: list[str] = Field(description="Step-by-step implementation plan.")
    difficulty_level: Literal["Beginner", "Medium", "Advanced"] = Field(
        description="Appropriate difficulty level (Beginner / Medium / Advanced)."
    )
    novelty_score: Literal["Low", "Medium", "High"] = Field(
        description="How novel this idea is relative to existing work."
    )
    feasibility_score: Literal["Low", "Medium", "High"] = Field(
        description="How practically achievable this project is for a student or small team."
    )
    generation_strategy: str = Field(
        description="Which ideation strategy produced this idea (e.g., Technology Fusion)."
    )
    target_audience: list[str] = Field(
        description="Best suited for (e.g., Students, Researchers, Startups)."
    )


class GeneratedIdeasOutput(BaseModel):
    generated_ideas: list[ProjectIdea]


# ---------------------------------------------------------------------------
# Strategy 1 — Technology Fusion
# ---------------------------------------------------------------------------

def _technology_fusion_signals(trend: TrendAnalysisOutput) -> list[dict]:
    """
    Build (tech_a, tech_b) pairs from suggested_combinations + trending topics.
    Returns a list of signal dicts consumed by the LLM prompt builder.
    """
    signals = []

    # Use explicit suggested combinations first
    for combo in trend.suggested_combinations:
        if len(combo) >= 2:
            signals.append({
                "strategy": "Technology Fusion",
                "tech_a": combo[0],
                "tech_b": combo[1],
            })

    # Supplement with cross-combinations of top trending × emerging
    emerging = trend.emerging_topics[:4]
    trending = trend.trending_topics[:4]
    for e, t in zip(emerging, trending):
        if e != t:
            signals.append({
                "strategy": "Technology Fusion",
                "tech_a": e,
                "tech_b": t,
            })

    return signals[:5]  # Cap to avoid prompt bloat


# ---------------------------------------------------------------------------
# Strategy 2 — Research Gap Exploitation
# ---------------------------------------------------------------------------

def _gap_exploitation_signals(trend: TrendAnalysisOutput) -> list[dict]:
    return [
        {"strategy": "Research Gap Exploitation", "gap": gap}
        for gap in trend.research_gaps[:4]
    ]


# ---------------------------------------------------------------------------
# Strategy 3 — Emerging Technology Application
# ---------------------------------------------------------------------------

def _emerging_tech_signals(trend: TrendAnalysisOutput) -> list[dict]:
    signals = []
    for topic in trend.emerging_topics[:4]:
        signals.append({
            "strategy": "Emerging Technology Application",
            "topic": topic,
        })
    return signals


# ---------------------------------------------------------------------------
# Strategy 4 — Cross-Cluster Innovation
# ---------------------------------------------------------------------------

def _cross_cluster_signals(trend: TrendAnalysisOutput) -> list[dict]:
    signals = []
    clusters = trend.topic_clusters
    if len(clusters) >= 2:
        for c1, c2 in combinations(clusters[:4], 2):
            signals.append({
                "strategy": "Cross-Cluster Innovation",
                "cluster_a": c1.cluster_name,
                "papers_a": c1.papers[:2],
                "cluster_b": c2.cluster_name,
                "papers_b": c2.papers[:2],
            })
    return signals[:3]


# ---------------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------------

_IDEA_SYSTEM_PROMPT = """\
You are a creative AI research strategist. Your role is to convert AI research signals into novel, actionable project ideas suitable for students, developers, and researchers.

For each research signal provided, generate exactly ONE unique project idea.

STRICT OUTPUT RULES:
- Output ONLY valid JSON — no markdown fences, no extra text.
- The JSON must match this schema exactly:

{
  "generated_ideas": [
    {
      "idea_title": "string",
      "problem_statement": "string",
      "solution": "string",
      "technologies_used": ["string"],
      "implementation_outline": ["string (step)"],
      "difficulty_level": "Beginner" | "Medium" | "Advanced",
      "novelty_score": "Low" | "Medium" | "High",
      "feasibility_score": "Low" | "Medium" | "High",
      "generation_strategy": "string",
      "target_audience": ["string"]
    }
  ]
}

Guidelines per idea:
- idea_title: Short, catchy, unique (max 8 words).
- problem_statement: A real-world pain point this project solves.
- solution: How modern AI/ML methods address the problem concretely.
- technologies_used: 3-5 specific technologies (e.g., LangChain, pgvector, Llama 3).
- implementation_outline: 4-6 concrete, ordered steps a developer would actually follow.
- difficulty_level: Based on implementation complexity.
- novelty_score: Based on how underexplored this intersection is.
- feasibility_score: Based on whether a student team can realistically build it.
- generation_strategy: The strategy name that produced this idea.
- target_audience: One or more of [Students, Developers, Researchers, Startups].

Do NOT repeat ideas. Each idea must address a different problem.
"""


def _build_user_prompt(signals: list[dict], trend: TrendAnalysisOutput) -> str:
    trend_summary = (
        f"Trending Topics: {', '.join(trend.trending_topics[:6])}\n"
        f"Emerging Topics: {', '.join(trend.emerging_topics[:4])}\n"
    )
    signals_text = json.dumps(signals, indent=2)
    return (
        f"Research Context:\n{trend_summary}\n"
        f"Research Signals (generate one idea per signal):\n{signals_text}\n\n"
        "Generate the JSON output now."
    )


# ---------------------------------------------------------------------------
# LLM Caller — Ollama (primary) + OpenAI-compatible (optional)
# ---------------------------------------------------------------------------

def _call_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str = "mistral",
    base_url: str = "http://localhost:11434",
) -> str | None:
    try:
        import requests

        resp = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.7, "num_predict": 2048},
            },
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        # Ollama wraps the response under message → content
        return data.get("message", {}).get("content", "")
    except Exception as exc:
        print(f"[WARN] Ollama LLM call failed: {exc}")
        return None


def _parse_json_safely(raw: str) -> dict | None:
    """Extract and parse the first JSON object found in a string."""
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
# Deterministic Fallback Idea Generator
# ---------------------------------------------------------------------------

_FALLBACK_TEMPLATES = [
    {
        "idea_title": "Multi-Agent RAG Research Assistant",
        "problem_statement": "Researchers waste hours manually reviewing papers to find answers to complex questions.",
        "solution": "Build a multi-agent system where specialized agents retrieve and synthesize information from a vector database using Retrieval Augmented Generation.",
        "technologies_used": ["LangChain", "ChromaDB", "Llama 3", "CrewAI", "SentenceTransformers"],
        "implementation_outline": [
            "Ingest research papers and chunk them",
            "Generate embeddings and store in ChromaDB",
            "Create retrieval agent with RAG pipeline",
            "Create synthesis agent to summarize and reason",
            "Orchestrate agents using CrewAI",
            "Build a simple web interface for queries",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Technology Fusion",
        "target_audience": ["Researchers", "Students"],
    },
    {
        "idea_title": "Memory-Persistent AI Study Companion",
        "problem_statement": "Existing AI tutors forget past sessions, making long-term personalized learning impossible.",
        "solution": "Develop an LLM-powered study assistant with episodic memory stored in a vector database, recalling past conversations and learning patterns.",
        "technologies_used": ["Ollama", "pgvector", "FastAPI", "LangChain Memory", "PostgreSQL"],
        "implementation_outline": [
            "Set up Ollama with a local LLM",
            "Design episodic memory schema in PostgreSQL with pgvector",
            "Build a memory manager that stores and retrieves past sessions",
            "Create a FastAPI backend for the chat interface",
            "Integrate long-term memory into the LLM context window",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Research Gap Exploitation",
        "target_audience": ["Students", "Developers"],
    },
    {
        "idea_title": "Knowledge Graph-Powered Literature Mapper",
        "problem_statement": "It is difficult to visualize how research concepts across papers relate to each other.",
        "solution": "Extract entities and relationships from papers to build a traversable knowledge graph, enabling multi-hop reasoning via LLMs for complex queries.",
        "technologies_used": ["spaCy", "Neo4j", "LangChain", "Llama 3", "NetworkX"],
        "implementation_outline": [
            "Parse and chunk research papers",
            "Use NLP to extract entities and relations",
            "Store the knowledge graph in Neo4j",
            "Implement a graph traversal module",
            "Use LLM to reason over retrieved subgraphs",
            "Visualize the knowledge graph in a web dashboard",
        ],
        "difficulty_level": "Advanced",
        "novelty_score": "High",
        "feasibility_score": "Medium",
        "generation_strategy": "Emerging Technology Application",
        "target_audience": ["Researchers", "Startups"],
    },
    {
        "idea_title": "Automated AI Hackathon Idea Generator",
        "problem_statement": "Students at hackathons struggle to come up with novel, technically feasible ideas under time pressure.",
        "solution": "A multi-agent pipeline that scrapes trending AI topics, clusters them, and generates novel project ideas with implementation outlines in real time.",
        "technologies_used": ["CrewAI", "Ollama", "Pydantic", "FastAPI", "Tailwind CSS"],
        "implementation_outline": [
            "Build a topic scraping agent for ArXiv and GitHub",
            "Implement trend analysis with keyword clustering",
            "Create an idea generation agent using LLM reasoning",
            "Score ideas by novelty and feasibility",
            "Serve results via a FastAPI + Tailwind web app",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Cross-Cluster Innovation",
        "target_audience": ["Students", "Developers"],
    },
    {
        "idea_title": "Multimodal Retrieval Augmented Debugger",
        "problem_statement": "Developers searching for solutions to programming errors get generic answers that ignore the visual context of their code and error screenshots.",
        "solution": "Combine vision-language models with a code-focused RAG system to allow developers to upload screenshots of errors and receive context-aware solutions.",
        "technologies_used": ["LLaVA", "LangChain", "FAISS", "FastAPI", "Python"],
        "implementation_outline": [
            "Set up LLaVA (vision-language model) via Ollama",
            "Ingest Stack Overflow posts and documentation into FAISS",
            "Accept image + text queries from the user",
            "Extract error text from image using OCR / LLaVA",
            "Retrieve relevant docs from FAISS",
            "Generate synthesized solution via LLM",
        ],
        "difficulty_level": "Advanced",
        "novelty_score": "High",
        "feasibility_score": "Medium",
        "generation_strategy": "Cross-Cluster Innovation",
        "target_audience": ["Developers", "Students"],
    },
]


def _deterministic_fallback(n_ideas: int = 3) -> GeneratedIdeasOutput:
    """Return a shuffled deterministic subset of fallback ideas."""
    random.shuffle(_FALLBACK_TEMPLATES)
    ideas = [ProjectIdea(**t) for t in _FALLBACK_TEMPLATES[:n_ideas]]
    return GeneratedIdeasOutput(generated_ideas=ideas)


# ---------------------------------------------------------------------------
# Diversity Filter — Remove near-duplicate ideas
# ---------------------------------------------------------------------------

def _deduplicate_ideas(ideas: list[ProjectIdea]) -> list[ProjectIdea]:
    """
    Remove ideas that share more than 60% of their technologies_used set.
    Keeps ideas that are distinctly different.
    """
    unique: list[ProjectIdea] = []
    for candidate in ideas:
        tech_set = set(t.lower() for t in candidate.technologies_used)
        is_duplicate = False
        for existing in unique:
            existing_set = set(t.lower() for t in existing.technologies_used)
            if len(tech_set) > 0 and len(existing_set) > 0:
                overlap = len(tech_set & existing_set) / min(len(tech_set), len(existing_set))
                if overlap > 0.6:
                    is_duplicate = True
                    break
        if not is_duplicate:
            unique.append(candidate)
    return unique


# ---------------------------------------------------------------------------
# Idea Ranking
# ---------------------------------------------------------------------------

_SCORE_MAP = {"Low": 1, "Medium": 2, "High": 3}


def _rank_ideas(ideas: list[ProjectIdea]) -> list[ProjectIdea]:
    """
    Rank ideas by a composite score: novelty (40%) + feasibility (40%) + difficulty penalty (20%)
    """
    def composite_score(idea: ProjectIdea) -> float:
        novelty = _SCORE_MAP.get(idea.novelty_score, 2)
        feasibility = _SCORE_MAP.get(idea.feasibility_score, 2)
        # Penalize ideas that are too hard (Advanced = 1 bonus, Beginner = 0 bonus, Medium = 1.5)
        difficulty_map = {"Beginner": 1.0, "Medium": 1.5, "Advanced": 1.0}
        diff_bonus = difficulty_map.get(idea.difficulty_level, 1.0)
        return novelty * 0.4 + feasibility * 0.4 + diff_bonus * 0.2

    return sorted(ideas, key=composite_score, reverse=True)


# ---------------------------------------------------------------------------
# Core Public Function
# ---------------------------------------------------------------------------

def generate_ideas(
    trend_report: dict | TrendAnalysisOutput,
    ollama_model: str = "mistral",
    ollama_base_url: str = "http://localhost:11434",
    n_ideas: int = 4,
) -> dict:
    """
    Core function: Transform a trend analysis report into novel AI project ideas.

    Args:
        trend_report:     Output from the Trend Analysis Agent (dict or model).
        ollama_model:     Ollama model name to use (default: llama3).
        ollama_base_url:  Ollama server address.
        n_ideas:          Target number of ideas to generate (3–5 recommended).

    Returns:
        JSON-serializable dict matching GeneratedIdeasOutput schema.
    """
    # Normalize input
    if isinstance(trend_report, dict):
        trend = TrendAnalysisOutput(**trend_report)
    else:
        trend = trend_report

    # Build research signals using all 4 strategies
    signals: list[dict] = []
    signals.extend(_technology_fusion_signals(trend))
    signals.extend(_gap_exploitation_signals(trend))
    signals.extend(_emerging_tech_signals(trend))
    signals.extend(_cross_cluster_signals(trend))

    # Trim to the target number of ideas
    signals = signals[:n_ideas]

    if not signals:
        print("[WARN] No signals generated from trend data — using deterministic fallback.")
        return _deterministic_fallback(n_ideas).model_dump()

    # Attempt LLM generation
    user_prompt = _build_user_prompt(signals, trend)
    raw_llm_output = _call_ollama(user_prompt=user_prompt, system_prompt=_IDEA_SYSTEM_PROMPT,
                                   model=ollama_model, base_url=ollama_base_url)

    parsed: dict | None = None
    if raw_llm_output:
        parsed = _parse_json_safely(raw_llm_output)

    # If LLM output is valid and contains ideas
    if parsed and "generated_ideas" in parsed and len(parsed["generated_ideas"]) > 0:
        try:
            output = GeneratedIdeasOutput(**parsed)
            ideas = output.generated_ideas
        except Exception as exc:
            print(f"[WARN] Pydantic validation failed on LLM output: {exc}. Using fallback.")
            ideas = _deterministic_fallback(n_ideas).generated_ideas
    else:
        print("[INFO] LLM did not return valid ideas. Using deterministic fallback.")
        ideas = _deterministic_fallback(n_ideas).generated_ideas

    # Post-processing: deduplicate → rank
    ideas = _deduplicate_ideas(ideas)
    ideas = _rank_ideas(ideas)
    ideas = ideas[:n_ideas]

    return GeneratedIdeasOutput(generated_ideas=ideas).model_dump()


# ---------------------------------------------------------------------------
# Main — Standalone Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Simulated input from the Trend Analysis Agent (matches actual output format)
    sample_trend_report = {
        "trending_topics": [
            "llm", "rag", "memory", "agents",
            "multi-agent systems", "tool use", "vector database", "embeddings"
        ],
        "emerging_topics": [
            "rag", "graph", "llm", "knowledge graph", "multi-hop reasoning"
        ],
        "research_gaps": [
            "Unexplored combination of llm and rag",
            "Unexplored combination of rag and memory",
            "Unexplored combination of memory and agents",
        ],
        "topic_clusters": [
            {
                "cluster_name": "Graph-based Retrieval",
                "papers": ["Graph RAG for Knowledge Retrieval", "Multimodal Retrieval with Vision-Language Models"],
            },
            {
                "cluster_name": "Multi-Agent Orchestration",
                "papers": ["Multi-Agent Orchestration for Complex Tasks", "AutoGen", "LangChain"],
            },
            {
                "cluster_name": "Memory Systems",
                "papers": ["Memory-Augmented Agents for Long-Horizon Tasks"],
            },
            {
                "cluster_name": "Vector Search",
                "papers": ["Efficient Vector Search at Scale", "Chroma"],
            },
        ],
        "suggested_combinations": [
            ["llm", "memory"],
            ["rag", "agents"],
            ["memory", "multi-agent systems"],
        ],
    }

    print("=" * 62)
    print("   Idea Generating Agent — Starting")
    print("=" * 62)

    result = generate_ideas(
        trend_report=sample_trend_report,
        ollama_model="mistral",
        ollama_base_url="http://localhost:11434",
        n_ideas=4,
    )

    print("\n" + "=" * 62)
    print("   GENERATED IDEAS")
    print("=" * 62)
    print(json.dumps(result, indent=2))
