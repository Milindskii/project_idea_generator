from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class UserSubmission(BaseModel):
    domain: str
    skill_level: str
    time_available: str
    goal: str
    idea_description: str
    submitted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProjectIdea(BaseModel):
    title: str
    description: str
    tech_stack: List[str]
    difficulty: str
    match_score: int


class AnalysisResult(BaseModel):
    analysis_text: str
    projects: List[ProjectIdea]
