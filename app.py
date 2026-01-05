from flask import Flask, request, jsonify
from flask_cors import CORS
import os, uuid, requests

from config import GEMINI_API_KEY, GEMINI_MODEL
from memory import MemoryManager
from file_reader import read_pdf, read_docx
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

memory = MemoryManager()

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

# -------------------------
# Upload File API
# -------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    session_id = str(uuid.uuid4())
    memory.create_session(session_id)

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, filename)
    file.save(file_path)

    if filename.lower().endswith(".pdf"):
        text = read_pdf(file_path)
    elif filename.lower().endswith(".docx"):
        text = read_docx(file_path)
    else:
        return jsonify({"error": "Only PDF or DOCX allowed"}), 400

    memory.store_document(session_id, text)

    return jsonify({
        "message": "File uploaded successfully",
        "session_id": session_id
    })

# -------------------------
# Chat API
# -------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id")
    question = data.get("question")

    if not session_id or not question:
        return jsonify({"error": "session_id and question required"}), 400

    context = memory.get_full_context(session_id)

    prompt = f"""
You are an AI assistant.
Answer ONLY based on the uploaded document.

{context}

User Question:
{question}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_URL, json=payload)

    if response.status_code != 200:
        return jsonify({"error": response.text}), 500

    answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
  #  print("----",response.json)
    memory.add_chat(session_id, "User", question)
    memory.add_chat(session_id, "Assistant", answer)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(port=5001,debug=True)