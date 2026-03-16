from __future__ import annotations

from models import AnalysisResult, ProjectIdea, UserSubmission


def _contains_any(haystack: str, needles: list[str]) -> bool:
    h = (haystack or "").lower()
    return any(n.lower() in h for n in needles)


def analyze_submission(data: UserSubmission) -> AnalysisResult:
    analysis_text = (
        f"Based on your interest in {data.domain} and your {data.skill_level} skill level, "
        f"your idea of '{data.idea_description}' shows strong potential. Given your {data.time_available} "
        f"timeline and goal to {data.goal}, here are your best matched project ideas."
    )

    domain = data.domain or ""

    if _contains_any(domain, ["ai", "artificial intelligence"]):
        projects = [
            ProjectIdea(
                title="Crop Disease Detector",
                description="A web app that detects crop diseases from leaf images and suggests treatments.",
                tech_stack=["Python", "TensorFlow", "Flask", "React"],
                difficulty="Intermediate",
                match_score=96,
            ),
            ProjectIdea(
                title="Student Performance Predictor",
                description="A small ML project to predict academic performance from study patterns and attendance.",
                tech_stack=["Python", "Scikit-learn", "Pandas", "Streamlit"],
                difficulty="Beginner",
                match_score=91,
            ),
            ProjectIdea(
                title="AI Chatbot for College FAQ",
                description="A retrieval-based chatbot that answers FAQs for students using a simple knowledge base.",
                tech_stack=["Python", "LangChain", "FastAPI", "React"],
                difficulty="Advanced",
                match_score=87,
            ),
        ]
    elif _contains_any(domain, ["web"]):
        projects = [
            ProjectIdea(
                title="Student Portfolio Builder",
                description="A guided portfolio generator with templates, hosting instructions, and export options.",
                tech_stack=["React", "Node.js", "MongoDB", "Tailwind"],
                difficulty="Beginner",
                match_score=95,
            ),
            ProjectIdea(
                title="College Event Management System",
                description="A full-stack app to create events, manage registrations, and send announcements.",
                tech_stack=["React", "FastAPI", "PostgreSQL"],
                difficulty="Intermediate",
                match_score=90,
            ),
            ProjectIdea(
                title="Online Exam Platform",
                description="A secure exam platform with timed tests, proctoring hooks, and analytics dashboards.",
                tech_stack=["Next.js", "Django", "Redis", "PostgreSQL"],
                difficulty="Advanced",
                match_score=85,
            ),
        ]
    elif _contains_any(domain, ["iot"]):
        projects = [
            ProjectIdea(
                title="Smart Attendance System",
                description="An IoT-backed attendance system using RFID/QR scans and a web dashboard for reports.",
                tech_stack=["Arduino", "Python", "MQTT", "React"],
                difficulty="Intermediate",
                match_score=93,
            ),
            ProjectIdea(
                title="Home Automation Dashboard",
                description="A dashboard to monitor and control home devices with simple rules and scenes.",
                tech_stack=["Raspberry Pi", "Python", "Node-RED", "React"],
                difficulty="Beginner",
                match_score=89,
            ),
            ProjectIdea(
                title="Industrial Equipment Monitor",
                description="A monitoring pipeline for equipment telemetry with alerts and historical graphs.",
                tech_stack=["ESP32", "Python", "InfluxDB", "Grafana"],
                difficulty="Advanced",
                match_score=84,
            ),
        ]
    else:
        projects = [
            ProjectIdea(
                title="Idea Validation Toolkit",
                description="A lightweight tool that helps you validate a project idea with checklists and scoring.",
                tech_stack=["React", "TypeScript", "FastAPI"],
                difficulty="Beginner",
                match_score=90,
            ),
            ProjectIdea(
                title="Workflow Automation Assistant",
                description="A small automation service that turns your inputs into repeatable task workflows.",
                tech_stack=["Python", "FastAPI", "SQLite"],
                difficulty="Intermediate",
                match_score=86,
            ),
            ProjectIdea(
                title="Community Resource Hub",
                description="A platform to collect, tag, and search domain-specific resources and project inspirations.",
                tech_stack=["Next.js", "PostgreSQL", "Prisma"],
                difficulty="Advanced",
                match_score=82,
            ),
        ]

    return AnalysisResult(analysis_text=analysis_text, projects=projects)
