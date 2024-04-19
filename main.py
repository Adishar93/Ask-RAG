from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os


# Loading API credentials
load_dotenv()

# global variables
global llm, template, vectorstore
vectorstore = None
llm = ChatOpenAI(model="gpt-3.5-turbo-0125")
template = """Use the following pieces of context to answer the question at the end. Use ONLY the context, do not make up your own answers.
    If the question is not related in any way or form to the data provided in context, say only this sentence 'Sorry, data regarding the same is not present in the PDF'.
    Use three sentences maximum and keep the answer as concise as possible.

    {context}

    Question: {question}

    Helpful Answer:"""


# Flask Server
app = Flask(__name__)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def split_text(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    return text_splitter.split_documents(docs)


# Endpoints
@app.route("/upload/process/pdf", methods=["POST"])
def upload_process_pdf():
    global llm, vectorstore
    uploaded_file = request.files["file"]

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file_contents = uploaded_file.read()
    storage_folder = "/temp"
    file_path = os.path.join(storage_folder, "file.pdf")

    if os.path.exists(file_path):
        # Delete the file
        os.remove(file_path)
        
    # Write the file to disk
    with open(file_path, "wb") as file:
        file.write(file_contents)

    loader = PyPDFLoader(os.path.join(storage_folder, "file.pdf"))
    docs = loader.load_and_split()

    all_splits = split_text(docs)
    print("DOCS DATA HAHAHAHAHAHAHAHHAHAHA:"+str(all_splits))

    vectorstore = FAISS.from_documents(
        documents=all_splits, embedding=OpenAIEmbeddings()
    )
    print("DOCS DATA HAHAHAHAHAHAHAHHAHAHA:"+str(vectorstore))
    response = jsonify({"message": "Request received successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200

@app.route('/ask/question', methods=['OPTIONS'])
def handle_preflight():
    # Add CORS headers to the response
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    return '', 204, headers

@app.route("/ask/question", methods=["POST"])
def answer_question():
    global template, vectorstore
    data = request.get_json()
    question = data.get("question")
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 6}
    )
    print(retriever.invoke(question))

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

    response = jsonify({"answer": finalAnswer})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(debug=False)
