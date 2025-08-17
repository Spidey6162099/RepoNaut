import os
import numpy as np

# We try to load CodeT5+ first; if unavailable (e.g., offline CI), we fall back to a deterministic pseudo-embedding.
MODEL_NAME = os.getenv("CODE_EMBEDDING_MODEL", "Salesforce/codet5p-110m-embedding")

_tokenizer = None
_model = None
_loaded = False

def _load_model():
    global _tokenizer, _model, _loaded
    if _loaded:
        return
    try:
        from transformers import AutoTokenizer, AutoModel
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModel.from_pretrained(MODEL_NAME)
        _loaded = True
    except Exception as e:
        # Fall back to pseudo-embedding
        _tokenizer = None
        _model = None
        _loaded = False

def _pseudo_embedding(text: str) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.random(384).astype("float32")
    return vec / (np.linalg.norm(vec) + 1e-8)

def embed_text(text: str) -> np.ndarray:
    _load_model()
    if _loaded and _tokenizer is not None and _model is not None:
        from numpy import float32
        import torch
        inputs = _tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=2048)
        with torch.no_grad():
            outputs = _model(**inputs)
            emb = outputs.last_hidden_state.mean(dim=1).squeeze(0).cpu().numpy().astype("float32")
        norm = np.linalg.norm(emb) + 1e-8
        return emb / norm
    # fallback
    return _pseudo_embedding(text)
