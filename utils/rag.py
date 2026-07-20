from utils.llm import llm
from utils.retriever import get_retriever


def ask_pdf(vectorstore, question):

    # Get retriever
    retriever = get_retriever(vectorstore)

    # Retrieve relevant documents
    docs = retriever.invoke(question)

    # Combine retrieved text into context
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    # Prompt
    prompt = f"""
You are StudyMate AI.

Answer the user's question ONLY using the provided context.

If the answer is not present in the context, reply:

"I couldn't find this information in the uploaded PDFs."

Context:
{context}

Question:
{question}

Answer:
"""

    # Generate response
    response = llm.invoke(prompt)

    return response.content, docs