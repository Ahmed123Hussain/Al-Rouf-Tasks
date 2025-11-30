import os
import glob
import time
import pickle
import argparse
from typing import List, Dict, Any
import numpy as np

from langdetect import detect
import transformers
from sentence_transformers import SentenceTransformer

try:
    import faiss
except Exception as e:
    raise ImportError("faiss is required. Install with `pip install faiss-cpu`") from e

# Optional OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

try:
    from flask import Flask, request, jsonify, render_template
except Exception:
    Flask = None

BASE_DIR = os.path.dirname(__file__)
DOCS_DIR = os.path.join(BASE_DIR, "docs")
INDEX_FILE = os.path.join(BASE_DIR, "index.faiss")
META_FILE = os.path.join(BASE_DIR, "index_meta.pkl")
EMB_MODEL_NAME = "all-MiniLM-L6-v2"


def load_text_files(doc_dir: str) -> List[Dict[str, Any]]:
    files = []
    for ext in ("*.txt", "*.md"):
        for path in glob.glob(os.path.join(doc_dir, ext)):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            files.append({"path": path, "text": text})
    return files


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


def build_index(model_name: str = EMB_MODEL_NAME):
    model = SentenceTransformer(model_name)
    if not os.path.exists(DOCS_DIR):
        raise FileNotFoundError(f"Docs folder not found: {DOCS_DIR}")
    docs = load_text_files(DOCS_DIR)
    meta = []
    embeddings = []

    for doc in docs:
        chunks = chunk_text(doc["text"], chunk_size=300, overlap=50)
        for idx, chunk in enumerate(chunks):
            emb = model.encode(chunk, show_progress_bar=False)
            embeddings.append(emb)
            meta.append({
                "source": os.path.basename(doc["path"]),
                "chunk_idx": idx,
                "text": chunk[:600],
            })

    if not embeddings:
        raise ValueError("No text chunks found in docs. Add .txt or .md files to ./docs")

    xb = np.vstack(embeddings).astype("float32")
    dim = xb.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(xb)
    index.add(xb)

    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, "wb") as f:
        pickle.dump(meta, f)

    return {"vectors": xb.shape[0], "dim": dim}


def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(META_FILE):
        raise FileNotFoundError("Index or meta not found. Run rebuild first.")
    index = faiss.read_index(INDEX_FILE)
    with open(META_FILE, "rb") as f:
        meta = pickle.load(f)
    return index, meta


def query_index(query: str, k: int = 3, model_name: str = EMB_MODEL_NAME) -> Dict[str, Any]:
    model = SentenceTransformer(model_name)
    index, meta = load_index()
    q_emb = model.encode(query).astype("float32")
    faiss.normalize_L2(q_emb.reshape(1, -1))
    D, I = index.search(q_emb.reshape(1, -1), k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        results.append({
            "score": float(score),
            "source": meta[idx]["source"],
            "chunk_idx": meta[idx]["chunk_idx"],
            "text": meta[idx]["text"],
        })
    return {"query": query, "lang": safe_detect_lang(query), "results": results}


def safe_detect_lang(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"


def synthesize_answer(query: str, chunks: List[Dict[str, Any]], max_tokens: int = 200) -> str:
    if not OPENAI_AVAILABLE or "OPENAI_API_KEY" not in os.environ:
        return "LLM synthesis not configured; returning cited passages instead."
    openai.api_key = os.environ["OPENAI_API_KEY"]
    prompt = (
        "You are a helpful assistant. Use the following source passages to answer the query. "
        "Cite each passage by filename and chunk index in square brackets.\n\n"
        f"Query: {query}\n\nSources:\n"
    )
    for c in chunks:
        prompt += f"[{c['source']} | chunk {c['chunk_idx']}]: {c['text']}\n\n"
    prompt += "\nProvide a concise answer in the same language as the query and include citations like [file.txt|chunk 0]."

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return resp["choices"][0]["message"]["content"].strip()


# The HTML template was moved to `templates/index.html`.
# The app uses Flask's `render_template('index.html')` to serve it.


def create_app():
    if Flask is None:
        raise ImportError('Flask not installed. Run: pip install flask')
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/rebuild', methods=['POST'])
    def rebuild():
        t0 = time.time()
        try:
            info = build_index()
            t1 = time.time()
            return jsonify({"status": "ok", "vectors": info["vectors"], "dim": info["dim"], "time": round(t1 - t0, 2)})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/query', methods=['POST'])
    def query():
        body = request.get_json() or {}
        q = body.get('query', '')
        k = int(body.get('k', 3))
        if not q:
            return jsonify({"status": "error", "message": "query required"}), 400
        t0 = time.time()
        try:
            res = query_index(q, k=k)
            t1 = time.time()
            return jsonify({"status": "ok", "query": res["query"], "lang": res["lang"], "results": res["results"], "time": round(t1 - t0, 2)})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app


def cli_main():
    parser = argparse.ArgumentParser(description="Single-file RAG web + CLI")
    parser.add_argument('--serve', action='store_true', help='Run web server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--rebuild', action='store_true')
    parser.add_argument('--query', type=str, help='Query the index from CLI')
    parser.add_argument('--k', type=int, default=3)
    args = parser.parse_args()

    if args.rebuild:
        t0 = time.time()
        info = build_index()
        t1 = time.time()
        print(f"Rebuilt index: {info['vectors']} vectors (dim={info['dim']}) in {t1-t0:.2f}s")
        return

    if args.query:
        t0 = time.time()
        res = query_index(args.query, k=args.k)
        t1 = time.time()
        print(f"Detected language: {res['lang']}")
        print(f"Query: {res['query']}\n")
        for i, r in enumerate(res['results'], 1):
            print(f"{i}. Source: {r['source']} (chunk {r['chunk_idx']}) — score {r['score']:.4f}")
            print(f"   \"{r['text'][:400]}\"")
        print('\n--- Report ---')
        print(f"Elapsed time: {t1-t0:.2f}s")
        return

    if args.serve:
        app = create_app()
        app.run(host=args.host, port=args.port)
        return

    parser.print_help()


if __name__ == '__main__':
    cli_main()