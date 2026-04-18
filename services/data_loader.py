import json
from langchain_core.documents import Document

def load_career_data():

    with open("data/career_roadmaps.json") as f:
        data = json.load(f)

    career_db = data["career_database"]["roles"]

    docs = []

    for role in career_db:

        role_name = role.get("role_name", "Unknown")

        content = f"""
Role: {role_name}

Career Details:
{json.dumps(role, indent=2)}
"""

        docs.append(
            Document(
                page_content=content,
                metadata={"role": role_name}
            )
        )

    return docs