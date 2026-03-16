from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_retriever():
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma(
        persist_directory="chroma_db",
        embedding_function=embedding
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return retriever