import json
from services.retriever import get_retriever


def load_careers():
    with open("data/career_roadmaps.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["career_database"]["roles"]


def retrieve_career_context(user_query: str):
    retriever = get_retriever()
    docs = retriever.invoke(user_query)
    return docs


def build_career_context(user_query: str) -> str:
    docs = retrieve_career_context(user_query)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context


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

    domain_bonus = 0
    for interest in user_interests:
        if interest and interest in career_domain:
            domain_bonus += 1

    description_bonus = 0
    for item in (user_skills | user_interests | user_subjects):
        if item and item in career_description:
            description_bonus += 1

    score = (
        4 * skill_match +
        3 * interest_tag_match +
        2 * subject_skill_match +
        2 * domain_bonus +
        1 * description_bonus
    )

    return score


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

    return top