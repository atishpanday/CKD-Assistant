from langchain.prompts import ChatPromptTemplate
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from utils.pinecone_client import get_pinecone_client, get_vector_store

from utils.llm import streaming_model, non_streaming_model

contextualize_q_system_prompt = """
Given a chat history and the latest user question
which might reference context in the chat history,
formulate a standalone question which can be understood
without the chat history. Do NOT answer the question, just
reformulate it if needed and otherwise return it as is."""

qa_system_prompt = """
Act as a helper to a physician or a nutritionist. If asked, you will tell the user that you are knowledgeable about CKD. DO NOT MENTION ANY WEBSITE. You will get health data from CKD patients on their vitals and symptoms.
Symptoms include- Ankle Swelling, Breathlessness, Increase in weight.
Vitals would include- Blood Pressure, spO2, Pulse Rate.
Looking at the data, in the chronological order, you have to tell the patients if their condition is progressing or better than before and also summarize it for their doctor in the form of a text document where you will tell them, these are the chronological changes in the patient's health data. And also recommend the doctor some drug changes and/or drug dose changes and/or dietary changes (if necessary) for the patient.
The doctor will validate the document.

For eg.
If patient's condition is progressing then increase the frusemide dose and the patient needs to monitor their condition more frequently and watch out for some other symptoms.

And also advise them to reduce the protein intake and reduce the fluid intake by 300 ml so as to avoid any volume overload.
\n\n
{context}"""


def call_chain(question, chat_history):
    sanitized_question = question.strip().replace("\n", " ")

    pc = get_pinecone_client()
    vector_store = get_vector_store(pc)
    retriever = vector_store.as_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            "\n{chat_history}\n",
            ("human", "{input}"),
        ]
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            "\n{chat_history}\n",
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm=non_streaming_model,
        retriever=retriever,
        prompt=contextualize_q_prompt,
    )

    question_answer_chain = create_stuff_documents_chain(
        llm=streaming_model, prompt=qa_prompt
    )

    rag_chain = create_retrieval_chain(
        retriever=history_aware_retriever,
        combine_docs_chain=question_answer_chain,
    )

    for chunk in rag_chain.stream(
        {
            "input": sanitized_question,
            "chat_history": chat_history,
        }
    ):
        if answer_chunk := chunk.get("answer"):
            yield answer_chunk
