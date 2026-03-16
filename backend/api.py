from fastapi import APIRouter
from .schemas import UserInputs, GenerationResponse, ProjectInfo

router = APIRouter()

@router.post("/generate-ideas", response_model=GenerationResponse)
async def generate_ideas(inputs: UserInputs):
    # This is where the core logic will go.
    # For now, we'll return a dynamic analysis based on inputs, 
    # but the projects are still based on the mock data logic.
    
    analysis = f"Based on your interest in {inputs.domain} and your {inputs.skillLevel} skill level, " \
               f"your idea relating to '{inputs.ideaDescription}' is highly feasible. " \
               f"It maps well to the concepts we discussed. Given your {inputs.timeframe} timeline, " \
               f"a focused MVP for {inputs.goal} is achievable."

    # In a real implementation, this would call an LLM or a more complex recommendation engine.
    projects = [
        ProjectInfo(
            id=1,
            title=f"{inputs.domain} Innovation Project",
            description=f"A specialized {inputs.domain} application focused on {inputs.ideaDescription}.",
            techStack=["Python", "FastAPI", "React"] if inputs.domain == "Web Dev" else ["Python", "TensorFlow", "React Native"],
            difficulty=inputs.skillLevel,
            matchScore=95
        ),
        ProjectInfo(
            id=2,
            title=f"{inputs.domain} Assistant",
            description=f"An automated tool for {inputs.ideaDescription} using {inputs.domain} principles.",
            techStack=["Node.js", "TypeScript", "PostgreSQL"],
            difficulty="Intermediate",
            matchScore=88
        ),
        ProjectInfo(
            id=3,
            title=f"{inputs.domain} Tracker",
            description=f"Management system for {inputs.ideaDescription}.",
            techStack=["Next.js", "TailwindCSS", "Supabase"],
            difficulty="Beginner",
            matchScore=82
        )
    ]

    return GenerationResponse(analysis=analysis, projects=projects)
