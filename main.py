import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from rag import answer_based_on_document, generate_and_save_vectorstore, get_vectorstore
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from utility import write_file, download_audio_from_youtube, transcribe_audio

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

    loader = PyPDFLoader(pdf_file_path)
    docs = loader.load_and_split()

    generate_and_save_vectorstore(storage_folder, docs)

    response = jsonify({"message": "Request received successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


# Endpoints
@app.route("/process/youtube", methods=["POST"])
def process_youtube():
    data = request.get_json()
    youtube_url = data.get('youtube_url')
    if not youtube_url:
        return jsonify({'error': 'No YouTube URL provided'}), 400

    try:
        audio_path = download_audio_from_youtube(youtube_url)
        print('Audio path:', audio_path)
    except Exception as e:
        return jsonify({'download youtube error': str(e)}), 500
    
    try:
        transcription = transcribe_audio(audio_path)
        transcription_document = [Document(page_content=transcription, metadata={})]
        generate_and_save_vectorstore(storage_folder, transcription_document)
        return jsonify({'transcription': transcription})
    except Exception as e:
        return jsonify({'transcribe audio error': str(e)}), 500

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
    app.run(debug=True)
