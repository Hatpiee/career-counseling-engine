import json
from langchain_core.messages import HumanMessage

def extract_profile(llm, message):

    prompt = f"""
Extract the user's profile from the text.

Return ONLY valid JSON in this format:

{{
  "skills": [],
  "interests": [],
  "subjects": []
}}

User text:
{message}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    text = response.content.strip()

    try:
        profile = json.loads(text)

    except json.JSONDecodeError:
        profile = {
            "skills": [],
            "interests": [],
            "subjects": []
        }

    return profile