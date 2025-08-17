from pathlib import Path

EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".idea", ".vscode"}
EXCLUDE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".lock", ".map", ".pdf", ".zip", ".min.js"}
INCLUDE_EXTS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".cpp", ".cc", ".cxx", ".c", ".rb", ".php", ".rs"
}

def is_relevant_file(path: Path) -> bool:
    if any(part in EXCLUDE_DIRS for part in path.parts):
        return False
    if path.suffix.lower() in EXCLUDE_EXTS:
        return False
    return path.suffix.lower() in INCLUDE_EXTS

def list_relevant_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and is_relevant_file(p)]
