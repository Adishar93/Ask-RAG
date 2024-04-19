import os
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


global llm, template
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
template = """Use the following pieces of context to answer the question at the end. Use ONLY the context, do not make up your own answers.
    If the question is not related in any way or form to the data provided in context, say only this sentence 'Sorry, data regarding the same is not present in the PDF'.
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


def generate_vectorstore(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load_and_split()

    all_splits = split_text(docs)
    vectorstore = FAISS.from_documents(
        documents=all_splits, embedding=OpenAIEmbeddings()
    )
    return vectorstore


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
