import json
import fitz
import tiktoken
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from openai import OpenAI
from scipy.spatial.distance import cosine

# Loading API credentials
load_dotenv()

# global variables
global df, embedding_model, embedding_encoding, system, client
system = "Only answer based on provided context, if not found in context say 'Sorry data is not there in PDF'"
client = OpenAI()
embedding_model = "text-embedding-ada-002"
embedding_encoding = "cl100k_base"

# Flask Server
app = Flask(__name__)


def process_text_to_chunks(text):
    # Split the text into chunks of 200 words
    words = text.split()
    sections = [" ".join(words[i : i + 200]) for i in range(0, len(words), 200)]

    # Overlap text sections
    sections_new = []
    window = 5  # number of segments to combine
    stride = 2  # number of segments to 'stride' over, used to create overlap
    for i in range(0, len(sections), stride):
        i_end = min(len(sections) - 1, i + window)
        text = " ".join(_ for _ in sections[i:i_end])
        sections_new.append(
            {
                "source": "PDF",
                "text": text,
            }
        )
    return sections_new


def process_chunks_to_embeddings(sections_new):
    global df, embedding_model, embedding_encoding
    # embedding model parameters
    max_tokens = 8000

    encoding = tiktoken.get_encoding(embedding_encoding)
    df = pd.DataFrame(sections_new)
    # Removing any row with empty text
    df = df[df.text.ne("")]
    # Counting the number of tokens for each text
    df["n_tokens"] = df.text.apply(lambda x: len(encoding.encode(str(x))))
    # filter too long text if any
    df = df[df.n_tokens <= max_tokens]
    df["embedding"] = df.text.apply(
        lambda x: client.embeddings.create(input=x, model=embedding_model)
        .data[0]
        .embedding
    )


def prepare_prompt(prompt, results):
    global embedding_encoding
    tokens_limit = 4096  # Limit for gpt-3.5-turbo
    # build our prompt with the retrieved contexts included
    user_start = "Answer the question only based on the context below.\n\n" + "Context:\n"
    user_end = f"\n\nQuestion: {prompt}\nAnswer:"

    encoding = tiktoken.get_encoding(embedding_encoding)

    count_of_tokens_consumed = len(
        encoding.encode(
            '"role":"system"' + ', "content" :"' + user_start + "\n\n---\n\n" + user_end
        )
    )
    count_of_tokens_for_context = tokens_limit - count_of_tokens_consumed
    contexts = ""
    # Fill in context as long as within limit
    for i in range(len(results)):
        if count_of_tokens_for_context >= results.n_tokens.iloc[i]:
            contexts += results.text.iloc[i] + "\n"
            count_of_tokens_for_context -= 1
            count_of_tokens_for_context -= results.n_tokens.iloc[i]

    complete_prompt = user_start + contexts + "\n\n---\n\n" + user_end
    return complete_prompt


def answer(messages):
    global client
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0.001
    )
    return response.choices[0].message.content


# Endpoints
@app.route("/upload/process/pdf", methods=["POST"])
def upload_process_pdf():
    uploaded_file = request.files["file"]

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file_contents = uploaded_file.read()  # Read the file contents directly

    # Parse text from the PDF
    try:
        doc = fitz.open(stream=file_contents, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
    except Exception as e:
        return jsonify({"error": "Failed to parse PDF", "details": str(e)}), 500
    print(text)
    chunks = process_text_to_chunks(text)
    process_chunks_to_embeddings(chunks)
    response = jsonify({"message": "Request received successfully"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response, 200


@app.route("/answer/question", methods=["POST"])
def answer_question():
    global client
    data = request.get_json()
    question = data.get("question")
    prompt_embedding = (
        client.embeddings.create(input=[question], model=embedding_model)
        .data[0]
        .embedding
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine(prompt_embedding, x))
    results = df.sort_values("similarity", ascending=False)
    print('results: ' + str(results))
    messages = [
        {"role": "system", "content": system},
    ]
    print('preparePrompt:s ' +  str(prepare_prompt(question, results)))
   
    messages.append({"role": "user", "content": prepare_prompt(question, results)})
    finalAnswer = answer(messages)
    print(finalAnswer)
    response = jsonify({"answer": finalAnswer})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == "__main__":
    app.run(debug=False)
