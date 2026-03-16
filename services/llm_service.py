import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_response(context, question):

    prompt = f"""
You are a career guidance assistant.

Use the provided career roadmap context to answer the user's question.

Context:
{context}

User Question:
{question}

Provide a clear career recommendation and explain why it suits the user.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content