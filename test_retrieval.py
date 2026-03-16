from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)

query = "I like AI, Python, and building chatbots"

results = vector_store.similarity_search(query, k=3)

print("\nTop matches:\n")

for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.metadata.get('role_name', 'Unknown')}")
    print(f"Domain: {doc.metadata.get('career_domain', 'Unknown')}")
    print(doc.page_content[:400])
    print("-" * 80)