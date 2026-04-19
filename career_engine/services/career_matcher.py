import json
from career_engine.services.retriever import get_retriever
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
CAREER_ENGINE_DIR = os.path.dirname(BASE_DIR)  

file_path = os.path.join(CAREER_ENGINE_DIR, "data", "career_roadmaps.json")


# ================= LOAD CAREERS =================
def load_careers():
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["career_database"]["roles"]


# ================= RETRIEVAL =================
def retrieve_career_context(user_query: str):
    retriever = get_retriever()
    docs = retriever.invoke(user_query)
    return docs


def build_career_context(user_query: str) -> str:
    docs = retrieve_career_context(user_query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context


# ================= MATCHING =================
def match_score(user_profile, career):
    if not isinstance(career, dict):
        return 0

    user_skills = set(s.strip().lower() for s in user_profile.get("skills", []))
    user_interests = set(i.strip().lower() for i in user_profile.get("interests", []))
    user_subjects = set(s.strip().lower() for s in user_profile.get("subjects", []))

    career_key_skills = set(s.strip().lower() for s in career.get("key_skills", []))
    career_tags = set(t.strip().lower() for t in career.get("tags", []))
    career_domain = career.get("career_domain", "").strip().lower()
    career_description = career.get("career_description", "").strip().lower()

    skill_match = len(user_skills & career_key_skills)
    interest_tag_match = len(user_interests & career_tags)
    subject_skill_match = len(user_subjects & career_key_skills)

    domain_bonus = sum(1 for interest in user_interests if interest in career_domain)

    description_bonus = sum(
        1 for item in (user_skills | user_interests | user_subjects)
        if item in career_description
    )

    score = (
        4 * skill_match +
        3 * interest_tag_match +
        2 * subject_skill_match +
        2 * domain_bonus +
        1 * description_bonus
    )

    return score


# ================= ROADMAP LOGIC =================

def extract_roadmap_steps(career):
    """
    Converts structured roadmap → simple step list
    """
    roadmap = career.get("roadmap", {})
    steps = []

    for section in ["foundations", "core_skills", "projects", "experience", "job_prep"]:
        if section in roadmap:
            for item in roadmap[section]:
                steps.append(item.get("step"))

    return steps[:6]  # limit for UI


def get_closest_roadmap(career_name, career_db):
    """
    Fallback for exploratory careers
    """
    name = career_name.lower()

    for career in career_db:
        if career["role_name"].lower() in name:
            return extract_roadmap_steps(career)

    # fallback: return generic AI roadmap if nothing matches
    return [
        "Learn fundamentals of programming (Python)",
        "Understand core domain basics",
        "Build beginner projects",
        "Advance to real-world applications",
        "Create portfolio",
        "Apply for internships"
    ]


def attach_roadmaps(careers, career_db):
    enriched = []

    for career in careers:
        role_name = career.get("role_name") or career.get("career")

        # grounded case
        if "roadmap" in career:
            steps = extract_roadmap_steps(career)

        # exploratory case
        else:
            steps = get_closest_roadmap(role_name, career_db)

        enriched.append({
            "career": role_name,
            "career_domain": career.get("career_domain", ""),
            "skills": career.get("key_skills", []),
            "roadmap": steps
        })

    return enriched


# ================= FINAL OUTPUT =================

def get_top_careers(user_profile, career_db):
    scored = []

    for career in career_db:
        if not isinstance(career, dict):
            continue

        score = match_score(user_profile, career)
        scored.append((career, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    top = []
    for career, score in scored[:3]:
        if isinstance(career, dict) and "role_name" in career:
            top.append(career)

    # 🔥 NEW: attach roadmap here
    top = attach_roadmaps(top, career_db)

    return top