from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analyzer import analyze_submission
from models import AnalysisResult, UserSubmission
from storage import SUBMISSIONS_DIR, save_submission


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
