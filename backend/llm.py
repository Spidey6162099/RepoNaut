import os
import requests
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

INSTRUCTIONS = (
    "You are a senior software engineer. Answer succinctly in natural language. "
    "Cite file paths and line ranges when useful. If unsure, say so."
)

def _gemini_answer(question: str, context_blocks: list[str]) -> str:
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    prompt = (
        f"{INSTRUCTIONS}\n\n"
        f"Question: {question}\n\n"
        "Relevant code context (each block has a file path header):\n\n" +
        "\n\n---\n\n".join(context_blocks) +
        "\n\nPlease answer with a brief explanation first, then bullet points with file references."
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(GEMINI_API_URL, headers=headers, params=params, data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def generate_answer(question: str, contexts: list[dict]) -> str:
    blocks = [f"File: {c['file']} (lines {c.get('start','?')}-{c.get('end','?')})\n\n{c['content']}" for c in contexts]
    if GEMINI_API_KEY:
        try:
            return _gemini_answer(question, blocks)
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Falling back to local heuristic.")
            # Fall through to local heuristic
    
    # Local heuristic fallback (no key or API error)
    if not contexts:
        return "I couldn't find relevant code in the index yet. Try ingesting the repository first."
    bullet_lines = []
    for c in contexts[:5]:
        bullet_lines.append(f"- `{c['file']}` lines {c.get('start','?')}-{c.get('end','?')}: looks related based on semantic similarity.")
    return "Here's what I found based on a semantic scan of the codebase:\n\n" + "\n".join(bullet_lines)
