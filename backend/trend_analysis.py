"""
Trend Analysis Agent
Part of the Multi-Agent AI Project Idea Generator

Pipeline:
  Research Data → Topic Extraction → Embedding Generation → Topic Clustering
  → Trend Frequency Analysis → Trend Velocity Calculation → Research Gap Detection
  → Structured Trend Output
"""

from __future__ import annotations

import json
import re
import warnings
from collections import Counter
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Data Models (Input + Output)
# ---------------------------------------------------------------------------

class Paper(BaseModel):
    title: str
    abstract: str = ""
    keywords: list[str] = Field(default_factory=list)
    year: int = 2024


class Repo(BaseModel):
    name: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    stars: int = 0


class ResearchData(BaseModel):
    papers: list[Paper] = Field(default_factory=list)
    repos: list[Repo] = Field(default_factory=list)


class TopicCluster(BaseModel):
    cluster_name: str
    papers: list[str]


class TrendAnalysisOutput(BaseModel):
    trending_topics: list[str]
    emerging_topics: list[str]
    research_gaps: list[str]
    topic_clusters: list[TopicCluster]
    suggested_combinations: list[list[str]]


# ---------------------------------------------------------------------------
# Stage 1 — Topic Extraction
# ---------------------------------------------------------------------------

def extract_topics(data: ResearchData) -> list[str]:
    """
    Extract raw topics from paper titles, keywords, and repo tags.
    This is deterministic (no LLM) to ensure no hallucination at this stage.
    """
    topics: list[str] = []

    for paper in data.papers:
        topics.append(paper.title)
        topics.extend(paper.keywords)

    for repo in data.repos:
        topics.append(repo.name)
        topics.extend(repo.tags)

    # Normalize
    normalized = [t.strip().lower() for t in topics if t and len(t.strip()) > 2]
    return normalized


# ---------------------------------------------------------------------------
# Stage 2 — Embedding Generation
# ---------------------------------------------------------------------------

def generate_embeddings(
    texts: list[str],
    ollama_model: str = "nomic-embed-text",
    ollama_base_url: str = "http://localhost:11434",
) -> np.ndarray:
    """
    Generate embeddings via Ollama's /api/embeddings endpoint (no torch needed).
    Falls back to TF-IDF if the Ollama call fails or Ollama is not running.

    To pull the embedding model once: `ollama pull nomic-embed-text`
    """
    if not texts:
        return np.empty((0, 128))

    try:
        import requests

        vectors = []
        for text in texts:
            resp = requests.post(
                f"{ollama_base_url}/api/embeddings",
                json={"model": ollama_model, "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            vectors.append(resp.json()["embedding"])

        return np.array(vectors, dtype=np.float32)

    except Exception as exc:
        print(f"[WARN] Ollama embeddings unavailable ({exc}). Falling back to TF-IDF.")
        from sklearn.feature_extraction.text import TfidfVectorizer

        vec = TfidfVectorizer(max_features=256)
        return vec.fit_transform(texts).toarray().astype(np.float32)


def get_corpus_texts(data: ResearchData) -> list[str]:
    """Build the list of text units to embed (title + abstract / description)."""
    corpus: list[str] = []
    for p in data.papers:
        corpus.append(f"{p.title}. {p.abstract}".strip())
    for r in data.repos:
        corpus.append(f"{r.name}. {r.description}".strip())
    return corpus


def get_corpus_labels(data: ResearchData) -> list[str]:
    """Return short labels (title / repo name) matching the corpus order."""
    labels: list[str] = []
    labels.extend(p.title for p in data.papers)
    labels.extend(r.name for r in data.repos)
    return labels


# ---------------------------------------------------------------------------
# Stage 3 — Topic Clustering
# ---------------------------------------------------------------------------

def cluster_topics(
    embeddings: np.ndarray,
    labels: list[str],
    n_clusters: int | None = None,
) -> list[tuple[int, str]]:
    """
    Cluster research items into thematic groups.
    Tries HDBSCAN first, then falls back to KMeans.

    Returns: list of (cluster_id, label) tuples.
    """
    if len(embeddings) == 0:
        return []

    # Auto-choose cluster count for KMeans
    if n_clusters is None:
        n_clusters = max(2, min(len(labels) // 2, 6))

    # Try HDBSCAN
    try:
        import hdbscan
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric="euclidean")
        cluster_ids = clusterer.fit_predict(embeddings)
        # HDBSCAN may return -1 (noise). Reassign noise to nearest centroid via KMeans.
        if -1 in cluster_ids:
            raise ValueError("HDBSCAN produced noise points; falling back to KMeans.")
        return list(zip(cluster_ids.tolist(), labels))
    except Exception:
        pass

    # Fallback: KMeans
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    cluster_ids = km.fit_predict(embeddings)
    return list(zip(cluster_ids.tolist(), labels))


def build_cluster_groups(
    cluster_assignments: list[tuple[int, str]],
) -> dict[int, list[str]]:
    """Group labels by cluster ID."""
    groups: dict[int, list[str]] = {}
    for cid, label in cluster_assignments:
        groups.setdefault(cid, []).append(label)
    return groups


# ---------------------------------------------------------------------------
# Stage 4 — Trend Frequency Analysis
# ---------------------------------------------------------------------------

def calculate_trend_frequency(data: ResearchData) -> list[tuple[str, float]]:
    """
    Compute normalized frequency scores for each keyword/topic.
    Repos are weighted by GitHub stars (log-scale).
    Returns list of (topic, score) sorted descending.
    """
    scores: Counter = Counter()

    # Paper keywords — each occurrence adds 1
    for paper in data.papers:
        for kw in paper.keywords:
            scores[kw.lower().strip()] += 1

    # Repo tags — weighted by log(stars + 1)
    for repo in data.repos:
        weight = 1 + np.log1p(repo.stars)
        for tag in repo.tags:
            scores[tag.lower().strip()] += weight

    total = sum(scores.values()) or 1
    ranked = [(topic, round(score / total, 4)) for topic, score in scores.most_common()]
    return ranked


# ---------------------------------------------------------------------------
# Stage 5 — Trend Velocity Analysis
# ---------------------------------------------------------------------------

def calculate_trend_velocity(data: ResearchData, current_year: int = 2024) -> dict[str, float]:
    """
    Velocity = recent_papers(topic) / total_papers(topic).
    'Recent' means within the last 2 years.
    Returns topic → velocity score.
    """
    recent_cutoff = current_year - 2
    topic_total: Counter = Counter()
    topic_recent: Counter = Counter()

    for paper in data.papers:
        for kw in paper.keywords:
            kw = kw.lower().strip()
            topic_total[kw] += 1
            if paper.year >= recent_cutoff:
                topic_recent[kw] += 1

    velocities = {}
    for topic, total in topic_total.items():
        recent = topic_recent.get(topic, 0)
        velocities[topic] = round(recent / total, 4)

    return velocities


# ---------------------------------------------------------------------------
# Stage 6 — LLM-Powered Gap Detection + Cluster Naming
# ---------------------------------------------------------------------------

_GAP_SYSTEM_PROMPT = """\
You are a research analysis assistant helping identify emerging trends.
You will be given structured research signals. Based ONLY on the provided information:

1. Name each cluster with a descriptive research theme (2-5 words).
2. List the top 5 research gaps or unmet opportunities.
3. Suggest 3 novel combinations of technologies that could lead to new projects.

Constraints:
- Do NOT invent topics absent from the data.
- Be concise and precise.
- Output MUST be valid JSON matching this schema exactly:

{
  "cluster_names": {"0": "...", "1": "..."},
  "research_gaps": ["gap 1", "gap 2", ...],
  "suggested_combinations": [["tech A", "tech B"], ...]
}
"""


def llm_gap_detection(
    cluster_groups: dict[int, list[str]],
    trending_topics: list[str],
    ollama_model: str = "mistral",
    base_url: str = "http://localhost:11434",
) -> dict[str, Any]:
    """
    Call local Ollama (or OpenAI-compatible) LLM for gap detection.
    Falls back to a deterministic result if the LLM call fails.
    """
    # Build a concise summary string for the LLM
    cluster_summary = {str(k): v for k, v in cluster_groups.items()}
    payload = json.dumps({
        "clusters": cluster_summary,
        "trending_topics": trending_topics[:10],
    }, indent=2)

    user_msg = f"Research signals:\n{payload}\n\nNow produce the JSON output."

    try:
        import requests
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": ollama_model,
                "messages": [
                    {"role": "system", "content": _GAP_SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2, "num_predict": 1024},
            },
            timeout=120,
        )
        content = response.json()["message"]["content"]
        # Extract JSON blob
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            return json.loads(m.group(0))
    except Exception as exc:
        print(f"[WARN] LLM call failed: {exc}. Using deterministic fallback.")

    # Deterministic fallback
    return {
        "cluster_names": {str(k): f"Cluster {k}" for k in cluster_groups},
        "research_gaps": [
            f"Unexplored combination of {trending_topics[i]} and {trending_topics[i+1]}"
            for i in range(min(3, len(trending_topics) - 1))
        ],
        "suggested_combinations": [
            [trending_topics[i], trending_topics[(i + 2) % len(trending_topics)]]
            for i in range(min(3, len(trending_topics)))
        ],
    }


# ---------------------------------------------------------------------------
# Orchestrator — Full Pipeline
# ---------------------------------------------------------------------------

class TrendAnalysisAgent:
    """
    Orchestrates the full trend analysis pipeline:
      Input (ResearchData) → Structured TrendAnalysisOutput
    """

    def __init__(
        self,
        ollama_model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        velocity_threshold: float = 0.6,
        top_k_trending: int = 10,
        current_year: int = 2024,
    ):
        self.ollama_model = ollama_model
        self.ollama_base_url = ollama_base_url
        self.velocity_threshold = velocity_threshold
        self.top_k_trending = top_k_trending
        self.current_year = current_year

    def run(self, research_data: ResearchData | dict) -> TrendAnalysisOutput:
        # Accept raw dict as well
        if isinstance(research_data, dict):
            research_data = ResearchData(**research_data)

        print("\n[1/6] Extracting topics …")
        raw_topics = extract_topics(research_data)

        print("[2/6] Generating embeddings …")
        corpus_texts = get_corpus_texts(research_data)
        corpus_labels = get_corpus_labels(research_data)

        if not corpus_texts:
            raise ValueError("No research data provided.")

        embeddings = generate_embeddings(
            corpus_texts,
            ollama_model="nomic-embed-text",
            ollama_base_url=self.ollama_base_url,
        )

        print("[3/6] Clustering topics …")
        assignments = cluster_topics(embeddings, corpus_labels)
        cluster_groups = build_cluster_groups(assignments)

        print("[4/6] Calculating trend frequency …")
        freq_ranked = calculate_trend_frequency(research_data)
        trending_topics = [t for t, _ in freq_ranked[: self.top_k_trending]]

        print("[5/6] Calculating trend velocity …")
        velocities = calculate_trend_velocity(research_data, self.current_year)
        emerging_topics = [
            t for t, v in sorted(velocities.items(), key=lambda x: -x[1])
            if v >= self.velocity_threshold
        ][:5]

        print("[6/6] Detecting research gaps via LLM …")
        llm_result = llm_gap_detection(
            cluster_groups=cluster_groups,
            trending_topics=trending_topics,
            ollama_model=self.ollama_model,
            base_url=self.ollama_base_url,
        )

        # Build named clusters
        cluster_names: dict[str, str] = llm_result.get("cluster_names", {})
        topic_clusters = [
            TopicCluster(
                cluster_name=cluster_names.get(str(cid), f"Cluster {cid}"),
                papers=papers,
            )
            for cid, papers in cluster_groups.items()
        ]

        return TrendAnalysisOutput(
            trending_topics=trending_topics,
            emerging_topics=emerging_topics,
            research_gaps=llm_result.get("research_gaps", []),
            topic_clusters=topic_clusters,
            suggested_combinations=llm_result.get("suggested_combinations", []),
        )


# ---------------------------------------------------------------------------
# Example Usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Rich test payload with diverse keywords and years
    sample_input = {
        "papers": [
            {
                "title": "Graph RAG for Knowledge Retrieval",
                "abstract": "We propose a graph-based retrieval-augmented generation framework that enables LLMs to traverse knowledge graphs for multi-hop reasoning.",
                "keywords": ["RAG", "Graph", "LLM", "Knowledge Graph", "Multi-hop Reasoning"],
                "year": 2024,
            },
            {
                "title": "Multi-Agent Orchestration for Complex Tasks",
                "abstract": "A framework for orchestrating multiple specialized AI agents using shared memory and tool-calling protocols.",
                "keywords": ["Multi-Agent Systems", "Tool Use", "LLM", "Orchestration"],
                "year": 2024,
            },
            {
                "title": "Multimodal Retrieval with Vision-Language Models",
                "abstract": "Extending dense retrieval to image-text pairs using contrastive pre-training and late interaction.",
                "keywords": ["Multimodal", "Vision-Language", "Retrieval", "Contrastive Learning"],
                "year": 2023,
            },
            {
                "title": "Memory-Augmented Agents for Long-Horizon Tasks",
                "abstract": "We introduce a persistent episodic memory module for LLM agents, enabling recall over multi-session interactions.",
                "keywords": ["Memory", "Agents", "LLM", "Episodic Memory", "Long-Horizon"],
                "year": 2024,
            },
            {
                "title": "Efficient Vector Search at Scale",
                "abstract": "A study of HNSW vs IVF-PQ indexing for billion-scale vector search in production RAG pipelines.",
                "keywords": ["Vector Database", "HNSW", "RAG", "Search", "FAISS"],
                "year": 2023,
            },
        ],
        "repos": [
            {
                "name": "GraphRAG",
                "description": "Graph-based retrieval augmented generation",
                "tags": ["RAG", "Graph", "LLM"],
                "stars": 3500,
            },
            {
                "name": "AutoGen",
                "description": "Multi-agent conversation framework by Microsoft",
                "tags": ["Multi-Agent Systems", "LLM", "Tool Use"],
                "stars": 28000,
            },
            {
                "name": "LangChain",
                "description": "Framework for developing LLM-powered applications with chains and agents",
                "tags": ["LLM", "Agents", "RAG", "Memory"],
                "stars": 90000,
            },
            {
                "name": "Chroma",
                "description": "The AI-native open-source vector database",
                "tags": ["Vector Database", "Embeddings", "RAG"],
                "stars": 14000,
            },
        ],
    }

    agent = TrendAnalysisAgent(
        ollama_model="mistral",
        ollama_base_url="http://localhost:11434",
        velocity_threshold=0.5,
        top_k_trending=8,
        current_year=2024,
    )

    print("=" * 60)
    print("   Trend Analysis Agent — Starting Pipeline")
    print("=" * 60)

    result: TrendAnalysisOutput = agent.run(sample_input)

    print("\n" + "=" * 60)
    print("   RESULTS")
    print("=" * 60)
    print(result.model_dump_json(indent=2))
