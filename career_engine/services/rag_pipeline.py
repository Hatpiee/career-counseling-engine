from services.retriever import get_retriever
from services.llm_service import generate_response


def career_query(question):

    retriever = get_retriever()

    docs = retriever.invoke(question)

    context = "\n\n".join([d.page_content for d in docs])

    answer = generate_response(context, question)

    return answer