import json

with open("data/career_roadmaps.json", "r", encoding="utf-8") as f:
    data = json.load(f)

roles = data["career_database"]["roles"]

documents = []

for role in roles:
    role_name = role.get("role_name", "")
    career_domain = role.get("career_domain", "")
    career_description = role.get("career_description", "")
    key_skills = ", ".join(role.get("key_skills", []))
    tags = ", ".join(role.get("tags", []))

    roadmap = role.get("roadmap", {})

    foundations = "; ".join([item.get("step", "") for item in roadmap.get("foundations", [])])
    core_skills = "; ".join([item.get("step", "") for item in roadmap.get("core_skills", [])])
    projects = "; ".join([item.get("step", "") for item in roadmap.get("projects", [])])
    experience = "; ".join([item.get("step", "") for item in roadmap.get("experience", [])])
    job_prep = "; ".join([item.get("step", "") for item in roadmap.get("job_prep", [])])

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

    documents.append({
        "id": role.get("id", ""),
        "role_name": role_name,
        "text": doc_text
    })

print("Total documents created:", len(documents))
print("\nSample document:\n")
print(documents[0]["text"])