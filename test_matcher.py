from services.career_matcher import retrieve_career_context

query = "I like AI, Python, and chatbots"

docs = retrieve_career_context(query)

for i, doc in enumerate(docs, 1):
    print(f"{i}. {doc.metadata.get('role_name', 'Unknown')}")
    print(f"Domain: {doc.metadata.get('career_domain', 'Unknown')}")
    print(doc.page_content[:300])
    print("-" * 80)