"""
NutriAI - SQLite Database Layer
Handles persistent storage for Users, Diet Sessions, Meal Plans, and Chat History.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger("nutriai.database")

# Database path in the data/ directory under workspace root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH  = os.path.join(DATA_DIR, "nutriai.db")


def get_connection() -> sqlite3.Connection:
    """Return a connection with Row factory and foreign keys enabled."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initialize database tables and indexes."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        # 2. Sessions Table (Stores 15-day plans and metadata)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                diet_plan_json TEXT,
                language TEXT DEFAULT 'ar',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );
        """)

        # 3. Messages Table (Chat conversation memory per session)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
            );
        """)

        # Indexes for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);")

        conn.commit()
    logger.info("NutriAI SQLite database initialized at: %s", DB_PATH)


# ══════════════════════════════════════════════════════════════════════════════
# USER OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by username."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if row:
            return dict(row)
        return None


def create_user(username: str, password: str, email: str) -> bool:
    """Create a new user. Returns True on success, False if user exists."""
    now = datetime.utcnow().isoformat()
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
                (username, password, email, now),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_all_users() -> List[Dict[str, Any]]:
    """Return all registered users (excluding password) for admin/defense review."""
    with get_connection() as conn:
        rows = conn.execute("SELECT username, email, created_at FROM users ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def create_session(session_id: str, username: str, language: str = "ar") -> None:
    """Create a new session record."""
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO sessions (session_id, username, diet_plan_json, language, created_at, updated_at)
            VALUES (?, ?, NULL, ?, ?, ?)
            """,
            (session_id, username, language, now, now),
        )
        conn.commit()


def get_session(session_id: str, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve full session data including parsed diet plan and history."""
    with get_connection() as conn:
        if username:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ? AND username = ?",
                (session_id, username)
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()

        if not row:
            return None

        data = dict(row)
        if data.get("diet_plan_json"):
            try:
                data["diet_plan"] = json.loads(data["diet_plan_json"])
            except Exception:
                data["diet_plan"] = None
        else:
            data["diet_plan"] = None

        # Fetch chat history for this session
        msg_rows = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        ).fetchall()
        data["history"] = [dict(m) for m in msg_rows]

        return data


def list_user_sessions(username: str) -> List[Dict[str, Any]]:
    """List all sessions for a user, with summary indicators."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.session_id, s.language, s.created_at, s.updated_at,
                   (s.diet_plan_json IS NOT NULL) AS has_plan,
                   COUNT(m.id) AS message_count
            FROM sessions s
            LEFT JOIN messages m ON s.session_id = m.session_id
            WHERE s.username = ?
            GROUP BY s.session_id
            ORDER BY s.created_at DESC
            """,
            (username,)
        ).fetchall()
        return [dict(r) for r in rows]


def save_session_plan(session_id: str, diet_plan: Dict[str, Any], language: str = "ar") -> None:
    """Save or update generated diet plan JSON in session."""
    now = datetime.utcnow().isoformat()
    plan_json = json.dumps(diet_plan, ensure_ascii=False)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE sessions
            SET diet_plan_json = ?, language = ?, updated_at = ?
            WHERE session_id = ?
            """,
            (plan_json, language, now, session_id),
        )
        conn.commit()


def delete_session(session_id: str, username: str) -> bool:
    """Delete a session belonging to user (cascades to messages)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ? AND username = ?", (session_id, username))
        conn.commit()
        return cursor.rowcount > 0


# ══════════════════════════════════════════════════════════════════════════════
# MESSAGE OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════

def add_message(session_id: str, role: str, content: str) -> None:
    """Append a single message (system, user, assistant) to session history."""
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, now),
        )
        conn.commit()


def get_messages(session_id: str) -> List[Dict[str, Any]]:
    """Fetch messages for a session."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content, created_at FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def clear_messages(session_id: str) -> None:
    """Clear messages for a session except initial system welcome."""
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ? AND role != 'system'", (session_id,))
        conn.commit()


# Auto-initialize tables upon module import
init_db()
