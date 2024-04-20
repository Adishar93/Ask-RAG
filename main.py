import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from rag import answer_based_on_document, generate_and_save_vectorstore, get_vectorstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from utility import write_file

# Loading API credentials
load_dotenv()

storage_folder = "/tmp"

# Flask Server
app = Flask(__name__)


# Endpoints
@app.route("/upload/process/pdf", methods=["POST"])
def upload_process_pdf():
    global storage_folder
    uploaded_file = request.files["file"]

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file_contents = uploaded_file.read()
    pdf_file_path = os.path.join(storage_folder, "file.pdf")

    write_file(pdf_file_path, file_contents)

    generate_and_save_vectorstore(storage_folder, pdf_file_path)

    response = jsonify({"message": "Request received successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


@app.route("/ask/question", methods=["OPTIONS"])
def handle_preflight():
    # Add CORS headers to the response
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return "", 204, headers


@app.route("/ask/question", methods=["POST"])
def answer_question():
    global vectorstore, storage_folder
    data = request.get_json()
    question = data.get("question")

    vectorstore = get_vectorstore(storage_folder)

    finalAnswer = answer_based_on_document(vectorstore, question)

    response = jsonify({"answer": finalAnswer})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(debug=False)
