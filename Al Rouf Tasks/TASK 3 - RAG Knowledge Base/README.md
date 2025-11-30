RAG Knowledge Base (AR/EN) — Single-file demo

What this is
- A compact single-file Python app (`main.py`) that ingests text files from `./docs`, chunks them, computes local embeddings with `sentence-transformers`, builds a FAISS index, and serves a minimal web UI (Flask) and CLI.
- Supports Arabic and English queries and returns top-k cited passages (filename + chunk index).

Files added
- `main.py` — single-file app (CLI + Flask web UI)
- `docs/sample_en_1.txt`, `docs/sample_en_2.txt`, `docs/sample_ar_1.txt` — sample documents
- `requirements.txt` — Python dependencies

Quick setup (PowerShell)

1) Create a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r .\requirements.txt
```

3) Rebuild the index (downloads embedding model on first run):

```powershell
python .\main.py --rebuild
```

4) Run the web UI:

```powershell
python .\main.py --serve
# then open http://127.0.0.1:5000 in your browser
```

5) Or query from CLI:

```powershell
python .\main.py --query "What is Al Rouf's mission?" --k 3
```

Optional: LLM synthesis
- If you want concise synthesized answers instead of raw passages, set the environment variable `OPENAI_API_KEY` and install the `openai` package. The app will call the ChatCompletion API when available.

Notes & tips
- The first `--rebuild` run downloads `all-MiniLM-L6-v2` (~100s depending on network) and may take some time to encode documents.
- Index files `index.faiss` and `index_meta.pkl` are saved to the project root.
- For low latency and cost control, embeddings are computed locally using `sentence-transformers`.

If you want, I can:
- Add a short test harness to validate queries programmatically.
- Improve the web UI to show synthesized answers (if OpenAI key provided) inline.
- Provide a small PowerShell script to automate setup.
