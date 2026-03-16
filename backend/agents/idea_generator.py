"""
agents/idea_generator.py

Idea Generating Agent — converts Trend Analysis insights into novel AI project ideas.

Strategies:
  1. Technology Fusion       — Combine multiple trending/emerging technologies
  2. Gap Exploitation        — Convert research gaps into project opportunities
  3. Emerging Tech App       — Apply emerging topics to real-world use cases
  4. Cross-Cluster Innovation — Bridge ideas from different research clusters
"""

from __future__ import annotations

import json
import re
import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.idea_schema import TrendReport, ProjectIdea

# ---------------------------------------------------------------------------
# Correct Technology Descriptions (prevents hallucination / misuse)
# ---------------------------------------------------------------------------

_TECH_GLOSSARY = {
    "rag": "Retrieval Augmented Generation (RAG) — retrieve relevant documents then use LLM to generate answers",
    "llm": "Large Language Model (LLM) — e.g., Llama 3, Mistral, GPT-4",
    "knowledge graph": "Knowledge Graph — structured graph of entities and relationships (e.g., Neo4j)",
    "multi-agent systems": "Multiple AI agents that collaborate, each with a specialized role",
    "vector database": "Vector Database — stores and retrieves embeddings (e.g., ChromaDB, pgvector, Pinecone)",
    "memory": "Agent/LLM memory — persistent storage of past interactions for personalization",
    "embeddings": "Vector representations of text used for semantic search and similarity",
    "graph": "Graph structures used for relational reasoning (e.g., knowledge graphs, GraphRAG)",
}

# ---------------------------------------------------------------------------
# LLM System Prompt — with strict terminology enforcement
# ---------------------------------------------------------------------------

_IDEA_SYSTEM_PROMPT = """You are an expert AI research strategist generating novel, implementable AI project ideas.

STRICT TERMINOLOGY RULES — use these EXACT definitions:
- RAG = Retrieval Augmented Generation (retrieve docs → LLM generates answer). NEVER "Relational Attention Graph".
- LLM = Large Language Model (e.g., Llama 3, Mistral, GPT-4).
- Knowledge Graph = structured entity-relationship graph database (e.g., Neo4j).
- Multi-Agent System = multiple AI agents collaborating with specialized roles.
- Vector Database = stores/retrieves text embeddings (e.g., ChromaDB, pgvector, Pinecone).

IDEA QUALITY RULES:
- Each idea solves a SPECIFIC, real-world problem.
- Implementable by students or developers in 2–4 weeks.
- Uses 3–5 AI technologies.
- No training large foundation models from scratch.
- Ideas must be for AI applications, research assistants, automation, or intelligent systems.

AVOID VAGUE IDEAS like "improve LLM training".
PREFER SPECIFIC IDEAS like "Multi-Agent Research Assistant using RAG and Memory".

OUTPUT: Return ONLY valid JSON (no markdown fences) matching this exact schema:
{
  "generated_ideas": [
    {
      "idea_title": "string (max 8 words)",
      "problem_statement": "string (specific real-world problem)",
      "solution": "string (concrete AI approach with correct tech)",
      "technologies_used": ["3-5 specific frameworks/tools"],
      "implementation_outline": ["4-6 ordered developer steps"],
      "difficulty_level": "Beginner" | "Medium" | "Advanced",
      "novelty_score": "Low" | "Medium" | "High",
      "feasibility_score": "Low" | "Medium" | "High",
      "generation_strategy": "string",
      "target_users": ["Students" | "Developers" | "Researchers" | "Startups"]
    }
  ]
}
Generate exactly one idea per research signal. Each idea must be distinct."""


def _build_signals(trend: TrendReport, n: int = 5) -> list[dict]:
    """Combine all 4 strategies into a unified signal list."""
    signals: list[dict] = []

    # Strategy 1: Technology Fusion (from suggested_combinations)
    for combo in trend.suggested_combinations[:3]:
        if len(combo) >= 2:
            signals.append({
                "strategy": "Technology Fusion",
                "description": f"Combine {combo[0].upper()} and {combo[1].upper()} to build a novel AI system.",
                "tech_a": combo[0],
                "tech_b": combo[1],
                "hint": _TECH_GLOSSARY.get(combo[0].lower(), combo[0]) + "; " + _TECH_GLOSSARY.get(combo[1].lower(), combo[1]),
            })

    # Strategy 2: Gap Exploitation
    for gap in trend.research_gaps[:3]:
        signals.append({
            "strategy": "Gap Exploitation",
            "description": f"Research gap: {gap}. Build a system that addresses this.",
            "gap": gap,
        })

    # Strategy 3: Emerging Tech Application
    for topic in trend.emerging_topics[:2]:
        signals.append({
            "strategy": "Emerging Tech Application",
            "description": f"Apply {topic} to a real-world problem domain.",
            "topic": topic,
            "definition": _TECH_GLOSSARY.get(topic.lower(), topic),
        })

    # Strategy 4: Cross-Cluster Innovation
    clusters = trend.topic_clusters
    if len(clusters) >= 2:
        c1, c2 = clusters[0], clusters[1]
        signals.append({
            "strategy": "Cross-Cluster Innovation",
            "description": f"Bridge '{c1.cluster_name}' and '{c2.cluster_name}' research themes.",
            "cluster_a": c1.cluster_name,
            "papers_a": c1.papers[:2],
            "cluster_b": c2.cluster_name,
            "papers_b": c2.papers[:2],
        })

    return signals[:n]


def _call_ollama(system: str, user: str, model: str, base_url: str) -> str | None:
    """Call Ollama chat endpoint and return raw content string."""
    try:
        import requests
        resp = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.65, "num_predict": 3000},
            },
            timeout=240,
        )
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "")
        print(f"[DEBUG] Raw LLM output (first 400 chars):\n{content[:400]}\n")
        return content
    except Exception as exc:
        print(f"[WARN] Ollama call failed: {exc}")
        return None


def _extract_json(text: str) -> dict | None:
    """Extract first JSON object from text, handling markdown fences."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


_DIFFICULTY_COERCE = {
    "easy": "Beginner", "beginner": "Beginner", "low": "Beginner",
    "medium": "Medium", "intermediate": "Medium", "moderate": "Medium",
    "hard": "Advanced", "advanced": "Advanced", "high": "Advanced", "difficult": "Advanced",
}
_LEVEL_COERCE = {
    "low": "Low", "medium": "Medium", "moderate": "Medium",
    "high": "High", "advanced": "High", "hard": "High",
}


def _coerce_idea(item: dict) -> dict:
    """Normalize enum fields before Pydantic validation."""
    if "difficulty_level" in item:
        item["difficulty_level"] = _DIFFICULTY_COERCE.get(
            str(item["difficulty_level"]).lower(), "Medium"
        )
    for field in ("novelty_score", "feasibility_score"):
        if field in item:
            item[field] = _LEVEL_COERCE.get(str(item[field]).lower(), "Medium")
    return item


# ---------------------------------------------------------------------------
# Deterministic Fallback Ideas (high-quality, hand-crafted)
# ---------------------------------------------------------------------------

_FALLBACK_IDEAS: list[dict] = [
    {
        "idea_title": "Personal Research Assistant with RAG and Memory",
        "problem_statement": "Students waste hours re-reading papers and lose track of what they've already learned across multiple study sessions.",
        "solution": "Build a Retrieval Augmented Generation (RAG) assistant that indexes the user's papers in a vector database and maintains episodic memory of past Q&A sessions. The LLM retrieves relevant paper chunks and uses stored memory to give personalized, context-aware answers.",
        "technologies_used": ["LangChain", "ChromaDB", "Llama 3 (via Ollama)", "FastAPI", "SQLite (for memory)"],
        "implementation_outline": [
            "Ingest research PDFs and chunk them into paragraphs",
            "Generate embeddings and store chunks in ChromaDB",
            "Implement RAG pipeline: retrieve top-k chunks → LLM answer",
            "Add session memory: store past questions and answers in SQLite",
            "Inject memory context into LLM prompt for personalization",
            "Build a simple chat API with FastAPI",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Gap Exploitation",
        "target_users": ["Students", "Researchers"],
    },
    {
        "idea_title": "Knowledge Graph-Powered Paper Summarizer",
        "problem_statement": "Reading large volumes of research papers is time-consuming; existing summarizers miss cross-paper relationships between concepts.",
        "solution": "Extract entities (authors, methods, datasets) and relationships from papers using NLP, build a Knowledge Graph (Neo4j), and let an LLM traverse the graph to answer complex multi-hop questions like 'Which papers use HNSW indexing in RAG systems?'",
        "technologies_used": ["spaCy (entity extraction)", "Neo4j (Knowledge Graph)", "LangChain", "Llama 3", "NetworkX"],
        "implementation_outline": [
            "Parse papers and run spaCy NER to extract entities and relations",
            "Store entity-relation triples in Neo4j",
            "Build a graph query module using NetworkX and Cypher",
            "Create an LLM agent that translates natural language to graph queries",
            "Return LLM-synthesized answers from the graph traversal results",
            "Add a web dashboard to visualize the knowledge graph",
        ],
        "difficulty_level": "Advanced",
        "novelty_score": "High",
        "feasibility_score": "Medium",
        "generation_strategy": "Cross-Cluster Innovation",
        "target_users": ["Researchers", "Startups"],
    },
    {
        "idea_title": "Multi-Agent Code Review and Bug Fix Assistant",
        "problem_statement": "Developers spend significant time on code reviews and debugging; single-agent tools like Copilot miss architectural issues visible only with multiple perspectives.",
        "solution": "Build a multi-agent system where a Reviewer Agent identifies bugs, a Security Agent checks for vulnerabilities, and a Fixer Agent proposes corrected code. Agents communicate via shared memory and a RAG knowledge base of best practices.",
        "technologies_used": ["CrewAI", "Llama 3 (via Ollama)", "RAG (ChromaDB)", "FastAPI", "Python AST"],
        "implementation_outline": [
            "Define three CrewAI agents: Reviewer, Security Analyst, Fixer",
            "Ingest coding best-practice docs into ChromaDB for RAG retrieval",
            "Reviewer Agent analyzes code using Python AST and LLM reasoning",
            "Security Agent flags common vulnerability patterns via RAG",
            "Fixer Agent receives flags and outputs corrected code",
            "Expose the workflow via a FastAPI endpoint accepting code snippets",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Technology Fusion",
        "target_users": ["Developers", "Students"],
    },
    {
        "idea_title": "Automated AI Project Idea Generator from ArXiv Trends",
        "problem_statement": "Students and hackathon participants struggle to come up with novel, technically valid AI project ideas under time pressure.",
        "solution": "A multi-agent pipeline that fetches recent ArXiv papers, extracts trending topics using embeddings and clustering, then uses an LLM to generate novel AI project ideas with full implementation plans — all automatically.",
        "technologies_used": ["CrewAI", "ArXiv API", "ChromaDB", "sentence-transformers", "Llama 3"],
        "implementation_outline": [
            "Fetch recent ArXiv papers via the ArXiv API",
            "Extract keywords and generate embeddings using sentence-transformers",
            "Cluster papers with KMeans to find research themes",
            "Feed cluster summaries to an LLM Idea Generator agent",
            "Output structured project ideas with tech stack and implementation plan",
            "Rank ideas by novelty and feasibility scores",
        ],
        "difficulty_level": "Medium",
        "novelty_score": "High",
        "feasibility_score": "High",
        "generation_strategy": "Emerging Tech Application",
        "target_users": ["Students", "Developers"],
    },
    {
        "idea_title": "Multimodal RAG System for Medical Image Reports",
        "problem_statement": "Medical professionals must manually cross-reference radiology images with clinical notes and literature — a slow, error-prone process.",
        "solution": "Combine vision-language model (LLaVA) with a RAG pipeline indexing medical guidelines. The system accepts an image + clinical note, retrieves relevant medical literature from a vector database, and generates a structured diagnosis summary.",
        "technologies_used": ["LLaVA (vision-language model)", "ChromaDB", "LangChain RAG", "FastAPI", "Tesseract OCR"],
        "implementation_outline": [
            "Set up LLaVA via Ollama for image understanding",
            "Ingest medical guidelines and literature into ChromaDB",
            "Accept radiology image + clinical note as input",
            "Extract text from image using Tesseract OCR",
            "Retrieve top-k relevant guideline chunks from ChromaDB via RAG",
            "Use LLaVA to synthesize image context + retrieved docs into a report",
        ],
        "difficulty_level": "Advanced",
        "novelty_score": "High",
        "feasibility_score": "Medium",
        "generation_strategy": "Cross-Cluster Innovation",
        "target_users": ["Researchers", "Startups"],
    },
]


def _deterministic_fallback(n: int = 4) -> list[ProjectIdea]:
    shuffled = _FALLBACK_IDEAS.copy()
    random.shuffle(shuffled)
    return [ProjectIdea(**t) for t in shuffled[:n]]


# ---------------------------------------------------------------------------
# Diversity Filter
# ---------------------------------------------------------------------------

def _deduplicate(ideas: list[ProjectIdea]) -> list[ProjectIdea]:
    """Remove ideas that share more than 60% of their technology set."""
    unique: list[ProjectIdea] = []
    for candidate in ideas:
        tech_set = {t.lower() for t in candidate.technologies_used}
        duplicate = False
        for existing in unique:
            existing_set = {t.lower() for t in existing.technologies_used}
            if tech_set and existing_set:
                overlap = len(tech_set & existing_set) / min(len(tech_set), len(existing_set))
                if overlap > 0.6:
                    duplicate = True
                    break
        if not duplicate:
            unique.append(candidate)
    return unique


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class IdeaGeneratorAgent:
    """
    Generates novel AI project ideas from trend analysis output.
    Uses Ollama LLM with a deterministic fallback for robustness.
    """

    def __init__(
        self,
        ollama_model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        n_ideas: int = 4,
    ):
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.n_ideas = n_ideas

    def run(self, trend_report: dict | TrendReport, user_context: str = "") -> list[ProjectIdea]:
        if isinstance(trend_report, dict):
            trend = TrendReport(**trend_report)
        else:
            trend = trend_report

        signals = _build_signals(trend, n=self.n_ideas)
        if not signals:
            print("[INFO] No signals found — using fallback ideas.")
            return _deterministic_fallback(self.n_ideas)

        # Build prompt
        trend_ctx = (
            f"Trending: {', '.join(trend.trending_topics[:6])}\n"
            f"Emerging: {', '.join(trend.emerging_topics[:4])}\n"
        )
        
        user_prompt = f"Research Context:\n{trend_ctx}\n"
        
        if user_context:
            user_prompt += f"\nUSER CONTEXT / REQUIREMENTS:\n{user_context}\n"
            
        user_prompt += f"\nGenerate one idea per signal:\n{json.dumps(signals, indent=2)}"

        raw = _call_ollama(_IDEA_SYSTEM_PROMPT, user_prompt, self.ollama_model, self.ollama_base_url)
        parsed = _extract_json(raw) if raw else None

        ideas: list[ProjectIdea] = []

        if parsed and "generated_ideas" in parsed:
            for item in parsed["generated_ideas"]:
                try:
                    coerced = _coerce_idea(item)
                    ideas.append(ProjectIdea(**coerced))
                except Exception as e:
                    print(f"[WARN] Skipped malformed idea: {e} | data: {item}")

        if not ideas:
            print("[INFO] LLM returned no valid ideas — using deterministic fallback.")
            ideas = _deterministic_fallback(self.n_ideas)

        ideas = _deduplicate(ideas)
        return ideas[: self.n_ideas]
