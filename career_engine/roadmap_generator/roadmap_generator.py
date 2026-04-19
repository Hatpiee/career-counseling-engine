def generate_roadmap(personalized_data):

    roadmap = []

    for stage, steps in personalized_data.items():

        roadmap.append({
            "stage": stage,
            "steps": steps
        })

    return roadmap