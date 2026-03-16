import json
from pathlib import Path
from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent
json_path = BASE_DIR / "data" / "career_roadmaps.json"

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

roles = data["career_roadmaps"]["roles"]

documents = []

for role in roles:
    role_id = role.get("id", "")
    role_name = role.get("role_name", "")
    career_domain = role.get("career_domain", "")
    career_description = role.get("career_description", "")
    key_skills = ", ".join(role.get("key_skills", []))
    tags = ", ".join(role.get("tags", []))

    roadmap = role.get("roadmap", {})

    foundations = "; ".join(item.get("step", "") for item in roadmap.get("foundations", []))
    core_skills = "; ".join(item.get("step", "") for item in roadmap.get("core_skills", []))
    projects = "; ".join(item.get("step", "") for item in roadmap.get("projects", []))
    experience = "; ".join(item.get("step", "") for item in roadmap.get("experience", []))
    job_prep = "; ".join(item.get("step", "") for item in roadmap.get("job_prep", []))

    doc_text = f"""
Role Name: {role_name}
Career Domain: {career_domain}
Career Description: {career_description}
Key Skills: {key_skills}
Tags: {tags}
Foundations: {foundations}
Core Skills: {core_skills}
Projects: {projects}
Experience: {experience}
Job Preparation: {job_prep}
""".strip()

    doc = Document(
        page_content=doc_text,
        metadata={
            "id": role_id,
            "role_name": role_name,
            "career_domain": career_domain
        }
    )

    documents.append(doc)

print("Total LangChain documents:", len(documents))
print("\nFirst document metadata:")
print(documents[0].metadata)
print("\nFirst document preview:\n")
print(documents[0].page_content[:700])