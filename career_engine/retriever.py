from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_store = Chroma(
    persist_directory="vector_db",
    embedding_function=embeddings
)


def retrieve_career_context(query: str):

    results = vector_store.similarity_search_with_score(query, k=3)

    careers = []

    for doc, score in results:
        careers.append({
            "content": doc.page_content,
            "score": float(score)
        })

    return careers