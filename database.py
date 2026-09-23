import sqlite3
from datetime import datetime

DATABASE = "masti_ai.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT DEFAULT 'New Chat',
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()


def create_conversation(title="New Chat"):
    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO conversations (title, created_at)
        VALUES (?, ?)
        """,
        (title, datetime.now().isoformat())
    )

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


def add_message(conversation_id, role, content):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            conversation_id,
            role,
            content,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_messages(conversation_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
        """,
        (conversation_id,)
    ).fetchall()

    conn.close()

    return [
        {
            "role": row["role"],
            "content": row["content"]
        }
        for row in rows
    ]
def get_conversations():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT id, title, created_at
        FROM conversations
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]


def get_conversation(conversation_id):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT id, title, created_at
        FROM conversations
        WHERE id = ?
        """,
        (conversation_id,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "created_at": row["created_at"]
    }