import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------------------------
# Pydantic Schemas for Structured Output
# -------------------------------------------------------------------

class SystemComponents(BaseModel):
    rag: Optional[str] = Field(
        description="RAG strategy and components (e.g., chunking strategy, embeddings model)."
    )
    agents: Optional[str] = Field(
        description="Multi-agent architecture, agent roles, and communication."
    )
    apis: Optional[str] = Field(
        description="Necessary APIs (internal microservices or external third-party APIs)."
    )
    vector_databases: Optional[str] = Field(
        description="Suggested vector databases (e.g., Pinecone, Weaviate, Milvus, pgvector)."
    )
    deployment_infrastructure: Optional[str] = Field(
        description="Cloud and deployment infrastructure (e.g., AWS, GCP, Vercel, Docker, Kubernetes)."
    )

class RoadmapMilestone(BaseModel):
    phase: str = Field(description="Name of the development phase (e.g., 'Phase 1: MVP & Core Pipeline').")
    tasks: List[str] = Field(description="Key actionable tasks to complete in this phase.")
    estimated_timeline: str = Field(description="Estimated time to complete this phase (e.g., '2 weeks').")

class YouTubeResource(BaseModel):
    title: str = Field(description="Title or topic of the educational resource.")
    search_query: str = Field(description="Ideal YouTube search query to find this resource (you can format this as a YouTube search URL).")
    description: str = Field(description="Why this concept is important for the user, tailored to their knowledge level.")

class ArchitectureImplementationPlan(BaseModel):
    user_knowledge_level: str = Field(
        description="Assessed knowledge level of the user (e.g., Beginner, Intermediate, Advanced) based on their prompt complexity."
    )
    ai_architecture: str = Field(
        description="High-level description of the chosen AI architecture and how data flows."
    )
    technology_stack: Dict[str, List[str]] = Field(
        description="Categorized tech stack (e.g., {'Frontend': ['Next.js', 'Tailwind'], 'Backend': ['FastAPI', 'Python'], 'AI': ['LangChain', 'Ollama']})."
    )
    system_components: SystemComponents
    development_roadmap: List[RoadmapMilestone]
    youtube_links_and_resources: List[YouTubeResource]

# -------------------------------------------------------------------
# CrewAI Implementation with Ollama
# -------------------------------------------------------------------

def get_architecture_agent_crew(user_prompt: str, agent1_insights: str, model_name: str = "mistral"):
    """
    Creates and returns a Crew configured to run the Architecture & Planning Agent using Ollama.
    """
    try:
        from crewai import Agent, Task, Crew, Process, LLM
    except ImportError:
        raise ImportError("CrewAI is not installed. Please install it using `pip install crewai`.")

    # Configure the Local Ollama LLM
    # Make sure Ollama is running locally and you have pulled the model (e.g., `ollama run llama3`)
    ollama_llm = LLM(
        model=f"ollama/{model_name}",
        base_url="http://localhost:11434"
    )

    # 1. Define the Agent
    architecture_agent = Agent(
        role="Architecture & Planning Agent",
        goal="Convert research insights from Agent 1 into a real, structured technical implementation plan.",
        backstory=(
            "You are an elite AI Software Architect. Your specialty is taking raw research insights "
            "and transforming them into robust, production-ready system designs. You carefully evaluate "
            "the user's technical knowledge based on their prompts to provide tailored advice and suitable "
            "YouTube educational resources to bridge their knowledge gaps. "
            "IMPORTANT: Do NOT use the ReAct format (Action/Observation/Thought). Just output the final JSON answer directly."
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=1,  # Prevent endless loops on local models
        llm=ollama_llm  # Bind the local Ollama LLM here
    )

    # 2. Define the Task
    architecture_task = Task(
        description=(
            "Analyze the user's original idea and the research insights provided by Agent 1.\n"
            "User Prompt: {user_prompt}\n"
            "Agent 1 Insights: {agent1_insights}\n\n"
            "Assess the user's technical knowledge based on the complexity of their prompt.\n"
            "Generate a complete AI architecture, a technology stack, and a step-by-step development roadmap.\n"
            "Clearly define all system components required such as RAG (including chunking/embedding strategies), "
            "Agents (roles and communication patterns), APIs, Vector Databases, and Deployment Infrastructure.\n"
            "Finally, provide a tailored list of YouTube resources specifically selected for the user's assessed knowledge level.\n\n"
            "CRITICAL INSTRUCTION: You MUST output ONLY valid JSON matching the following schema. "
            "Do not include any intro, outro, or conversational text. Your entire response must be parseable by `json.loads()`.\n\n"
            "Required JSON Schema:\n"
            "{\n"
            "  \"user_knowledge_level\": \"string (e.g., Beginner, Intermediate, Advanced)\",\n"
            "  \"ai_architecture\": \"string (high-level data flow)\",\n"
            "  \"technology_stack\": { \"Frontend\": [\"str\"], \"Backend\": [\"str\"], \"AI\": [\"str\"] },\n"
            "  \"system_components\": {\n"
            "    \"rag\": \"string (or null)\",\n"
            "    \"agents\": \"string (or null)\",\n"
            "    \"apis\": \"string (or null)\",\n"
            "    \"vector_databases\": \"string (or null)\",\n"
            "    \"deployment_infrastructure\": \"string (or null)\"\n"
            "  },\n"
            "  \"development_roadmap\": [\n"
            "    {\n"
            "      \"phase\": \"string\",\n"
            "      \"tasks\": [\"string\"],\n"
            "      \"estimated_timeline\": \"string\"\n"
            "    }\n"
            "  ],\n"
            "  \"youtube_links_and_resources\": [\n"
            "    {\n"
            "      \"title\": \"string\",\n"
            "      \"search_query\": \"string\",\n"
            "      \"description\": \"string\"\n"
            "    }\n"
            "  ]\n"
            "}\n"
        ),
        expected_output="A strict JSON object matching the provided schema exactly.",
        agent=architecture_agent,
        # Remove output_pydantic as local small LLMs often struggle natively with function calling / tools
    )

    # 3. Assemble the Crew
    crew = Crew(
        agents=[architecture_agent],
        tasks=[architecture_task],
        process=Process.sequential,
        verbose=True
    )

    return crew, architecture_task

# -------------------------------------------------------------------
# Example Usage / Testing
# -------------------------------------------------------------------
if __name__ == "__main__":
    
    # Example using Llama 3 (or change to 'mistral', 'phi3' etc that you have pulled in Ollama)
    OLLAMA_MODEL = "mistral"
    print(f"Make sure Ollama is running and you have pulled the model: `ollama run {OLLAMA_MODEL}`")

    mock_user_prompt = "I want to build a website that generates innovative product ideas for curious students."

    mock_agent1_insights = """
Idea generation platforms commonly use large language models to create structured product concepts.
Techniques include brainstorming prompts, SCAMPER innovation framework, and problem-solution ideation.

Students benefit from guided creativity tools that transform interests or real-world problems into product ideas.

Possible features:
- idea generation based on interests
- problem discovery prompts
- idea scoring and feedback
- startup-style pitch summaries

Relevant inspiration sources include Product Hunt listings, startup databases, and innovation case studies.
"""

    import json

    try:
        # Create the crew
        crew, task = get_architecture_agent_crew(
            user_prompt=mock_user_prompt, 
            agent1_insights=mock_agent1_insights,
            model_name=OLLAMA_MODEL
        )
        
        # Execute the crew
        print(f"Starting the Architecture & Planning Crew via {OLLAMA_MODEL}...")
        result = crew.kickoff(inputs={
            "user_prompt": mock_user_prompt,
            "agent1_insights": mock_agent1_insights
        })
        
        raw_output = str(result)
        
        # Super simple cleanup to parse the JSON output from Ollama
        import re
        json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        
        if json_match:
            parsed_json = json.loads(json_match.group(0))
            
            # Use Pydantic to validate the JSON output
            plan_data = ArchitectureImplementationPlan(**parsed_json)
            
            print("\n✅ Successfully generated structured plan:\n")
            print(f"User Knowledge Level: {plan_data.user_knowledge_level}")
            print(f"Architecture: {plan_data.ai_architecture}")
            print(f"\nFull Output JSON:\n{plan_data.model_dump_json(indent=2)}")
        else:
            print("\n❌ Failed to parse JSON from output. Raw Output:\n", raw_output)

    except Exception as e:
        print(f"Error running CrewAI with Ollama: {e}")