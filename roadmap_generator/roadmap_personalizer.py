difficulty_rank = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3
}


def personalize(dataset, profile):

    role = profile.get("role")

    roles = dataset.get("career_database", {}).get("roles", [])

    role_data = None

    for r in roles:
        if r.get("id") == role:
            role_data = r
            break

    if role_data is None:
        return {}

    roadmap = role_data.get("roadmap", {})

    personalized_roadmap = {}

    for section, steps in roadmap.items():

        filtered_steps = []

        for step in steps:

            # CASE 1: step is a dictionary
            if isinstance(step, dict):

                title = step.get("title", "")
                difficulty = step.get("difficulty", "beginner").lower()

                filtered_steps.append({
                    "title": title,
                    "difficulty": difficulty
                })

            # CASE 2: step is just a string
            elif isinstance(step, str):

                filtered_steps.append({
                    "title": step,
                    "difficulty": "beginner"
                })

        personalized_roadmap[section] = filtered_steps

    return personalized_roadmap