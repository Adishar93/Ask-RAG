import os
import cloud_storage_client
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

global llm, question_template
llm = ChatOpenAI(
    model="gpt-3.5-turbo-0125"
)
question_template = """Use the following pieces of context to answer the question at the end. Use ONLY the context, do not make up your own answers.
    If the question is not related in any way or form to the data provided in context, say only this sentence 'Your question isn't answerable using the PDF or video you provided, sorry!'.
    Use three sentences maximum and keep the answer as concise as possible. if the question mentions 'video' or 'PDF' it refers to the context provided.

    {context}

    Question: {question}

    Helpful Answer:"""

medical_summarization_template = """Summarize the following text into meaningful bullet points considering it contains patient doctor consultation conversation summarize it for the patient:
"{text}"
Summary:"""


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
    global question_template
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 6}
    )
    custom_rag_prompt = PromptTemplate.from_template(question_template)
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

def summarize_medical_consultation(text):
    global medical_summarization_template
    custom_summary_prompt = PromptTemplate.from_template(medical_summarization_template)
    llm_chain = LLMChain(llm=llm, prompt=custom_summary_prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")
    text_document = Document(page_content=text)
    finalAnswer = ""
    for chunk in stuff_chain.stream([text_document]):
        finalAnswer += chunk["output_text"]

    return finalAnswer
