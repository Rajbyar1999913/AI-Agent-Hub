import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "agent_memory.sqlite3"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    return conn


def save_memory(category: str, content: str) -> str:
    category = category.strip()[:80]
    content = content.strip()[:4000]
    if not category or not content:
        raise ValueError("Category and content are required.")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO memories(category, content) VALUES (?, ?)",
            (category, content),
        )
    return "Memory saved."


def search_memory(query: str, limit: int = 10) -> str:
    query = query.strip()
    if not query:
        return "No memory query provided."
    limit = max(1, min(limit, 20))
    pattern = f"%{query}%"
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT category, content, created_at
            FROM memories
            WHERE category LIKE ? OR content LIKE ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (pattern, pattern, limit),
        ).fetchall()
    if not rows:
        return "No matching memories."
    return "\n".join(
        f"[{created_at}] {category}: {content}"
        for category, content, created_at in rows
    )
