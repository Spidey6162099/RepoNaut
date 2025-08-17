import shutil
import json
import logging
import faiss
import numpy as np
import tempfile
import time

from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from git import Repo, GitCommandError

from filters import list_relevant_files
from parser import chunk_file
from embeddings import embed_text
from query import search_code

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Semantic Code Query API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

ROOT = Path(__file__).parent
DATA = ROOT / "data"
INDEX_FILE = DATA / "vectors.faiss"
META_FILE = DATA / "metadata.json"

# This is no longer used for the workspace, but for storing the final index
DATA.mkdir(parents=True, exist_ok=True)

# Map file extensions to language names supported by the parser
EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".java": "java",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".cc": "cpp",
    ".c": "cpp", # Using cpp parser for c as it's largely compatible
    ".cs": "c_sharp",
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_repo(github_url: str = Form(...)):
    """
    Ingests a repository by cloning it into a temporary directory,
    processing its files, creating embeddings, and building a FAISS index.
    This approach is reliable and avoids persistent file lock issues.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            logger.info(f"Created temporary directory for ingestion: {temp_dir}")

            if github_url.startswith("http") or github_url.endswith(".git"):
                # Clone remote repo into the temporary directory
                Repo.clone_from(github_url, repo_root)
            else:
                # For local paths, copy the tree into the temporary directory
                # to provide isolation from the source.
                src = Path(github_url)
                if not src.is_dir():
                    raise HTTPException(status_code=400, detail=f"Local path not found or not a directory: {src}")
                shutil.copytree(src, repo_root, dirs_exist_ok=True)

            # --- File processing starts here ---
            records = []
            logger.info("Scanning for relevant files in temporary directory...")
            for fp in list_relevant_files(repo_root):
                lang = EXT_TO_LANG.get(fp.suffix.lower())
                if not lang:
                    continue

                try:
                    content = fp.read_text(encoding="utf-8", errors="ignore")
                    chunks = chunk_file(content, lang)
                    for ch in chunks:
                        text = ch["content"].strip()
                        if not text:
                            continue
                        records.append({
                            "file": str(fp.relative_to(repo_root)),
                            "start": ch["start_line"],
                            "end": ch["end_line"],
                            "content": text[:2000]  # preview limit
                        })
                except Exception as e:
                    logger.warning(f"Could not process file {fp}: {e}")
            
            # The 'with' block automatically deletes temp_dir upon exit.
            # We must build the index before that happens.
            if not records:
                # Clear any old index if no new records were found
                if INDEX_FILE.exists(): INDEX_FILE.unlink()
                if META_FILE.exists(): META_FILE.unlink()
                return {"status": "ok", "chunks": 0}

            logger.info(f"Extracted {len(records)} chunks. Building FAISS index.")
            vecs = np.vstack([embed_text(r["content"]) for r in records]).astype("float32")
            index = faiss.IndexFlatL2(vecs.shape[1])
            index.add(vecs)
            
            faiss.write_index(index, str(INDEX_FILE))
            META_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

            file_count = len({r['file'] for r in records})
            logger.info(f"Ingestion complete. Indexed {len(records)} chunks from {file_count} files.")
            return {"status": "ingestion complete", "files": file_count, "chunks": len(records)}

    except GitCommandError as e:
        raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e.stderr}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")


@app.post("/query")
def query_repo(query: str = Form(...), k: int = Form(6)):
    if not INDEX_FILE.exists() or not META_FILE.exists():
        raise HTTPException(status_code=404, detail="Index not built; please ingest a repository first.")
    return search_code(query, str(INDEX_FILE), str(META_FILE), int(k))