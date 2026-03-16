import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "chatbot.db"

_db: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """Get the database connection (singleton pattern)."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
        _db.row_factory = aiosqlite.Row
    return _db


async def close_db() -> None:
    """Close the database connection."""
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def get_connection() -> aiosqlite.Connection:
    """Get a database connection."""
    return await get_db()


async def init_db() -> None:
    """Initialize the database with required tables."""
    conn = await get_db()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
    """)
    await conn.commit()


async def create_session(title: str = "New Chat") -> int:
    """Create a new chat session and return its ID."""
    now = datetime.utcnow().isoformat()
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO chat_sessions (title, created_at, updated_at) VALUES (?, ?, ?)",
        (title, now, now)
    )
    await conn.commit()
    return cursor.lastrowid


async def list_sessions() -> list[dict]:
    """List all chat sessions ordered by updated_at DESC."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, title, created_at, updated_at FROM chat_sessions ORDER BY updated_at DESC"
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def delete_session(session_id: int) -> None:
    """Delete a chat session and all its messages."""
    conn = await get_db()
    await conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    await conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    await conn.commit()


async def rename_session(session_id: int, title: str) -> None:
    """Rename a chat session."""
    conn = await get_db()
    await conn.execute(
        "UPDATE chat_sessions SET title = ? WHERE id = ?",
        (title, session_id)
    )
    await conn.commit()


async def get_messages(session_id: int) -> list[dict]:
    """Get all messages for a session."""
    conn = await get_db()
    cursor = await conn.execute(
        "SELECT id, session_id, role, content, created_at FROM messages WHERE session_id = ? ORDER BY created_at ASC",
        (session_id,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def add_message(session_id: int, role: str, content: str) -> int:
    """Add a message to a session and return its ID."""
    now = datetime.utcnow().isoformat()
    conn = await get_db()
    cursor = await conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, now)
    )
    await conn.commit()
    return cursor.lastrowid


async def update_session_timestamp(session_id: int) -> None:
    """Update the updated_at timestamp for a session."""
    now = datetime.utcnow().isoformat()
    conn = await get_db()
    await conn.execute(
        "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
        (now, session_id)
    )
    await conn.commit()
