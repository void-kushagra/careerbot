from sentence_transformers import SentenceTransformer
import pandas as pd
import faiss
import numpy as np
from flask import Flask, request, jsonify, render_template
from fuzzywuzzy import fuzz

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load dataset
df = pd.read_csv("dataset.csv")

# ✅ Fill NaNs with empty strings
df = df.fillna("")

# Combine relevant fields into one text
texts = (
    df["name"] + ". Fields: " + df["fields"] +
    ". Background: " + df["background"] +
    ". Skills: " + df["skills"] +
    ". Advice: " + df["advice"] +
    ". Future scope: " + df["future_scope"]
).tolist()

# Generate embeddings
print("Embedding dataset... please wait ⏳")
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

# Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"answer": "Please enter a valid query."})

    # Embed query and search
    q_emb = model.encode([question]).astype("float32")
    distances, indices = index.search(q_emb, k=1)

    idx = indices[0][0]
    score = 100 - distances[0][0]  # similarity estimate

    # Fuzzy match with names to avoid irrelevant mapping
    best_match_score = 0
    best_match_idx = None
    for i, name in enumerate(df["name"]):
        match_score = fuzz.partial_ratio(question.lower(), name.lower())
        if match_score > best_match_score:
            best_match_score = match_score
            best_match_idx = i

    # Use fuzzy result if more relevant than embedding
    if best_match_score > 70:
        idx = best_match_idx

    # Optional threshold for very poor matches
    if distances[0][0] > 30 and best_match_score < 50:
        return jsonify({"answer": "Sorry, couldn't understand. Try rephrasing your query."})

    row = df.iloc[idx]
    answer = (
        f"Career: {row['name']}\n"
        f"Fields: {row['fields']}\n"
        f"Background: {row['background']}\n"
        f"Skills: {row['skills']}\n"
        f"Advice: {row['advice']}\n"
        f"Future scope: {row['future_scope']}"
    )
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
