EXTENSION_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".h": "cpp",
    ".cs": "csharp",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".sql": "sql",
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".md": "markdown",
}

def detect_language(file_path: str) -> str:
    from pathlib import Path
    ext = Path(file_path).suffix.lower()
    return EXTENSION_MAP.get(ext, "unknown")