career_keywords = {
    "machine_learning_engineer": [
        "ai engineer",
        "ai architect",
        "ml engineer",
        "machine learning engineer"
    ],

    "data_scientist": [
        "data scientist",
        "data science"
    ],

    "software_engineer": [
        "software engineer",
        "software developer",
        "developer"
    ]
}
company_keywords = [
    "google",
    "amazon",
    "microsoft",
    "meta",
    "apple",
    "netflix"
]
education_keywords = {
    "first year": "1st_year",
    "second year": "2nd_year",
    "third year": "3rd_year",
    "final year": "final_year"
}

skill_keywords = {
    "beginner": "beginner",
    "intermediate": "intermediate",
    "advanced": "advanced"
}

def extract_entities(text):

    education_level = None
    skill_level = "beginner"

    for key in education_keywords:
        if key in text:
            education_level = education_keywords[key]

    for key in skill_keywords:
        if key in text:
            skill_level = skill_keywords[key]
    target_companies = []

    for company in company_keywords:
        if company in text:
            target_companies.append(company)

    career_goal = None

    for role, keywords in career_keywords.items():
        for keyword in keywords:
            if keyword in text:
               career_goal = role

    return {
        "career_goal": career_goal,
        "education_level": education_level,
        "skill_level": skill_level,
        "target_companies": target_companies,
        
    }