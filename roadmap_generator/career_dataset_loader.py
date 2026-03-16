import json


def normalize_role_name(name):
    return name.lower().replace(" ", "_")


def load_dataset():

    with open("data/career_roadmaps.json", "r", encoding="utf-8") as f:
        raw = json.load(f)

    dataset = {}

    for role in raw["career_database"]["roles"]:

        role_key = normalize_role_name(role["role_name"])

        roadmap = role["roadmap"]

        dataset[role_key] = {
            "foundations": roadmap.get("foundations", []),
            "core_skills": roadmap.get("core_skills", []),
            "projects": roadmap.get("projects", []),
            "internships": roadmap.get("experience", []),
            "job_preparation": roadmap.get("job_prep", [])
        }

    return dataset