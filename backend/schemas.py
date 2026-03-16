from pydantic import BaseModel
from typing import List, Optional

class UserInputs(BaseModel):
    domain: str
    skillLevel: str
    timeframe: str
    goal: str
    ideaDescription: str

class ProjectInfo(BaseModel):
    id: int
    title: str
    description: str
    techStack: List[str]
    difficulty: str
    matchScore: int

class GenerationResponse(BaseModel):
    analysis: str
    projects: List[ProjectInfo]
