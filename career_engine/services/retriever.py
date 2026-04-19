from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vector_store = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return retriever