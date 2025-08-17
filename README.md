# RepoNaut:Semantic Code Query & Summarization

Language-aware code search using Tree-sitter + FAISS with a React frontend,
**CodeT5+ embeddings** for semantic retrieval, and **Gemini Pro** (optional) for natural language answers.

## Prerequisites
- Python 3.11+
- Node 18+
- Git
<!-- - (Optional) Docker -->

## Backend (Local)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional: set your Gemini key for richer answers
export GEMINI_API_KEY=YOUR_KEY_HERE  # Windows: set GEMINI_API_KEY=YOUR_KEY_HERE
uvicorn main:app --reload --port 8000
```
Backend: http://localhost:8000/docs

> If the CodeT5 model isn't available locally, it will download the first time.
> If you're offline, the system falls back to a deterministic embedding so it still works.

## Frontend (Local)
```bash
cd frontend
npm i
npm run dev
```
Frontend: http://localhost:5173

<!-- ## Docker (Frontend + Backend)
```bash
docker compose up --build
```
- API: http://localhost:8000
- Web: http://localhost:5173 -->

## Using the App
1) Paste a **GitHub URL or local path** and click **Ingest**.
2) Ask a question in natural language.
3) You'll get a **natural language answer** (Gemini if key provided, otherwise a local heuristic) and the **relevant code snippets** retrieved via FAISS.

## Tests
### Backend
```bash
cd backend
pytest -q
```
### Frontend
```bash
cd frontend
npm test
```

## Environment
- `GEMINI_API_KEY` – optional; if set, answers come from Gemini Pro. Otherwise a local summarized answer is used.
- `CODE_EMBEDDING_MODEL` – defaults to `Salesforce/codet5p-110m-embedding`.

## Notes
- Tree-sitter grammars are bundled via `tree_sitter_languages` (no manual compile).
- Extend `parser.py` `NODE_TYPES`/languages to support more structures.
- Increase `k` (top-K) via the frontend API file if needed.
