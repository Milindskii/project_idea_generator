import json
import os
from datetime import datetime
import ollama

from arxiv_rag_tool import arxiv_research_tool
from github_repo_tool import search_github_repos

MODEL = "mistral"


def build_prompt(query, papers, repos):

    paper_context = ""

    for p in papers:
        paper_context += f"""
Title: {p['paper_title']}
Summary: {p['content']}
"""

    repo_context = ""

    for r in repos:
        repo_context += f"""
Repo: {r['name']}
Description: {r['description']}
Stars: {r['stars']}
"""

    prompt = f"""
You are an AI research analysis system.

Your task is to convert research knowledge into structured JSON.

Return EXACTLY this schema:

{{
  "query": "{query}",
  "timestamp": "",
  "papers": [],
  "github_repositories": [],
  "aggregated_topics": [],
  "methods": [],
  "datasets": [],
  "tools": []
}}

Research Papers:
{paper_context}

GitHub Repositories:
{repo_context}

Rules:
- Only output JSON
- No explanation text
- Do not change schema
"""

    return prompt


import re

def run_llm(prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Return valid JSON only. Do not wrap in markdown or backticks."},
            {"role": "user", "content": prompt}
        ],
        options={"temperature": 0.2}
    )

    text = response["message"]["content"]
    
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return m.group(0)
    return "{}"

def save_json(data):

    path = os.path.join(os.path.dirname(__file__), "research_output.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("Saved:", path)


def research_agent(query):

    print("Collecting research papers...")

    papers = arxiv_research_tool(query)

    print("Searching GitHub repositories...")

    repos = search_github_repos(query)

    print("Running LLM analysis...")

    prompt = build_prompt(query, papers, repos)

    output = run_llm(prompt)

    try:
        structured = json.loads(output)
    except:
        print("Invalid JSON returned")
        print(output)
        return

    # Ensure the LLM didn't drop the raw data
    structured["query"] = query
    structured["timestamp"] = str(datetime.now().date())
    
    if "papers" not in structured or not structured["papers"]:
        structured["papers"] = papers
        
    if "github_repositories" not in structured or not structured["github_repositories"]:
        structured["github_repositories"] = repos

    save_json(structured)

    return structured, papers, repos


if __name__ == "__main__":

    query = input("Enter research query: ")

    research_agent(query)