import json
import numpy as np
import faiss
from embeddings import embed_text
from llm import generate_answer

def search_code(query: str, index_file: str, meta_file: str, k: int = 6):
    index = faiss.read_index(index_file)
    with open(meta_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    q = embed_text(query).reshape(1, -1).astype("float32")
    D, I = index.search(q, k)
    matches = []
    for idx, score in zip(I[0], D[0]):
        if 0 <= idx < len(metadata):
            item = dict(metadata[idx])
            item["score"] = float(score)
            matches.append(item)
    answer = generate_answer(query, matches)
    # Trim snippet length to avoid oversized payloads in UI
    for m in matches:
        if "content" in m and len(m["content"]) > 1600:
            m["content"] = m["content"][:1600] + "\n..."
    return {"answer": answer, "matches": matches}
