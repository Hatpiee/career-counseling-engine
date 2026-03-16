from services.career_matcher import build_career_context

query = "I like AI, Python, and chatbots"

context = build_career_context(query)

print(context)