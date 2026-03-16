from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_submission
from models_simple import AnalysisResult, ProjectIdea, UserSubmission
from storage import SUBMISSIONS_DIR, save_submission

# Multi‑agent pipeline pieces
from trend_analysis import TrendAnalysisAgent, ResearchData, Paper, Repo
from pipeline.idea_pipeline import IdeaPipeline
from agent1_research.research_agent import research_agent


app = FastAPI(title="IdeaSpark API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "IdeaSpark API running"}


@app.get("/api/submissions")
def list_submissions():
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([p.name for p in SUBMISSIONS_DIR.glob("submission_*.json") if p.is_file()])
    return files


@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze(submission: UserSubmission):
    filename = save_submission(submission.model_dump())
    # Artificial delay so the analyzing screen feels real
    await asyncio.sleep(2)
    result = analyze_submission(submission)
    return result


@app.post("/api/full_pipeline", response_model=AnalysisResult)
async def full_pipeline(submission: UserSubmission):
    """
    Run the full multi‑agent pipeline (research → trend analysis → idea generation → ranking)
    and map the result into the simple AnalysisResult schema used by the frontend.
    Falls back to the basic analyzer if anything in the pipeline fails.
    """
    # Always persist the raw submission
    save_submission(submission.model_dump())

    try:
        # 0. Use the user's idea / goal as the research query
        query = (
            (submission.idea_description or "").strip()
            or (submission.goal or "").strip()
            or (submission.domain or "").strip()
            or "novel AI project ideas"
        )

        # Phase 0: Research agent (Arxiv + GitHub)
        research_result = research_agent(query)
        if not research_result:
            raise RuntimeError("Research agent failed")
        structured, raw_papers, raw_repos = research_result

        # Convert raw papers + repos into ResearchData for trend analysis
        papers = [
            Paper(
                title=p.get("paper_title", p.get("title", "Unknown Title")),
                abstract=p.get("content", p.get("abstract", p.get("summary", ""))),
                keywords=[kw.strip() for kw in p.get("keywords", []) if isinstance(kw, str)],
                year=2024,
            )
            for p in raw_papers
        ]

        repos = [
            Repo(
                name=r.get("name", r.get("repo", "Unknown Repo")),
                description=r.get("description", ""),
                tags=[t.strip() for t in r.get("tags", []) if isinstance(t, str)],
                stars=int(r.get("stars", 0) or 0),
            )
            for r in raw_repos
        ]

        research_data = ResearchData(papers=papers, repos=repos)

        # Phase 1: Trend analysis
        trend_agent = TrendAnalysisAgent(
            ollama_model="mistral",
            ollama_base_url="http://localhost:11434",
            velocity_threshold=0.5,
            top_k_trending=8,
            current_year=2024,
        )
        trend_output = trend_agent.run(research_data)

        # Phase 2: Idea generation + ranking pipeline
        pipeline = IdeaPipeline(
            ollama_model="mistral",
            ollama_base_url="http://localhost:11434",
            n_ideas=5,
            top_k=3,
            use_llm_scoring=True,
        )

        user_context = (
            f"User domain: {submission.domain}; "
            f"skill level: {submission.skill_level}; "
            f"goal: {submission.goal}; "
            f"time available: {submission.time_available}."
        )

        pipeline_result = pipeline.run(trend_output.model_dump(), user_context=user_context)

        # Build simple projects list for the frontend from ranked ideas
        projects: list[ProjectIdea] = []
        for ranked in pipeline_result.ranked_ideas:
            idea = next((i for i in pipeline_result.generated_ideas if i.idea_title == ranked.idea_title), None)

            description = getattr(idea, "solution", None) if idea is not None else ranked.justification
            tech_stack = getattr(idea, "technologies_used", None) if idea is not None else []
            difficulty = getattr(idea, "difficulty_level", None) if idea is not None else "Medium"

            # Map 0–10 score to an approximate 0–100 match percentage
            match_score = int(round(ranked.final_score * 10))

            projects.append(
                ProjectIdea(
                    title=ranked.idea_title,
                    description=description,
                    tech_stack=list(tech_stack or []),
                    difficulty=str(difficulty),
                    match_score=match_score,
                )
            )

        analysis_text = (
            "Using a full multi‑agent research pipeline (papers + GitHub repos → "
            "trend analysis → idea generation → ranking), we generated and scored "
            f"{len(projects)} project ideas tailored to your context."
        )

        # Artificial delay so the analyzing screen feels real
        await asyncio.sleep(2)

        return AnalysisResult(analysis_text=analysis_text, projects=projects)

    except Exception:
        # If anything in the advanced pipeline fails (e.g., Ollama not running,
        # missing ML libs, network issues), gracefully fall back to the simple analyzer.
        await asyncio.sleep(2)
        return analyze_submission(submission)
