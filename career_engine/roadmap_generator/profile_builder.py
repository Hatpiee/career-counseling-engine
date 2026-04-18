def build_profile(role, entities):

    profile = {
        "career_role": role,
        "education_level": entities.get("education_level"),
        "skill_level": entities.get("skill_level", "beginner"),
        "target_companies": entities.get("target_companies", [])
    }

    return profile