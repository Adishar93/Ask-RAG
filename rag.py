import os
import cloud_storage_client
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

global llm, template
llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125"
)
template = """Use the following pieces of context to answer the question at the end. Use ONLY the context, do not make up your own answers.
    If the question is not related in any way or form to the data provided in context, say only this sentence 'Your question isn't answerable using the PDF you uploaded, sorry!'.
    Use three sentences maximum and keep the answer as concise as possible.

    {context}

    Question: {question}

    Helpful Answer:"""


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def split_text(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    return text_splitter.split_documents(docs)


def generate_and_save_vectorstore(storage_folder, docs):
    
    all_splits = split_text(docs)
    vectorstore = FAISS.from_documents(
        documents=all_splits, embedding=OpenAIEmbeddings()
    )

    # Delete existing files if they exist before writing
    if os.path.exists(os.path.join(storage_folder, "vectordata/index.faiss")):
        os.remove(os.path.join(storage_folder, "vectordata/index.faiss"))
    if os.path.exists(os.path.join(storage_folder, "vectordata/index.pkl")):
        os.remove(os.path.join(storage_folder, "vectordata/index.pkl"))

    vectorstore.save_local(os.path.join(storage_folder, "vectordata"))
    # Upload files to Google Cloud
    cloud_storage_client.upload_file_to_location(
        os.path.join(storage_folder, "vectordata"), "index.faiss", "index.faiss"
    )
    cloud_storage_client.upload_file_to_location(
        os.path.join(storage_folder, "vectordata"), "index.pkl", "index.pkl"
    )


def get_vectorstore(storage_folder):
    cloud_storage_client.download_file_from_location(
        os.path.join(storage_folder, "vectordata"), "index.faiss", "index.faiss"
    )
    cloud_storage_client.download_file_from_location(
        os.path.join(storage_folder, "vectordata"), "index.pkl", "index.pkl"
    )
    return FAISS.load_local(
        os.path.join(storage_folder, "vectordata"),
        OpenAIEmbeddings(),
        allow_dangerous_deserialization=True,
    )


def answer_based_on_document(vectorstore, question):
    global template
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 6}
    )
    custom_rag_prompt = PromptTemplate.from_template(template)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )

    finalAnswer = ""
    for chunk in rag_chain.stream(question):
        finalAnswer += chunk

    return finalAnswer
