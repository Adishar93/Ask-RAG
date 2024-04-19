import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from rag import answer_based_on_document, generate_vectorstore
from utility import write_file


# Loading API credentials
load_dotenv()

# Flask Server
app = Flask(__name__)


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

    write_file(file_path, file_contents)

    vectorstore = generate_vectorstore(file_path)

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

    finalAnswer = answer_based_on_document(question)

    response = jsonify({"answer": finalAnswer})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(debug=False)
