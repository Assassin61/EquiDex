import sqlite3
import json
from datetime import datetime


class SQLiteAdapter:
    def __init__(self, config: dict):
        self.db_path = config["database"]["path"]
        self._initialize_db()

    def _initialize_db(self):
        """
        Creates tables if they don't exist yet.
        Runs once on startup.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT,
                name TEXT,
                age INTEGER,
                ethnicity TEXT,
                experience REAL,
                gpa REAL,
                name_origin TEXT,
                age_group TEXT,
                qualification_score REAL,
                decision TEXT,
                score REAL,
                timestamp TEXT,
                source TEXT DEFAULT 'demo'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT,
                timestamp TEXT,
                total_processed INTEGER,
                status TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT,
                timestamp TEXT,
                analysis TEXT,
                formal_report TEXT,
                summary TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save(self, collection: str, record: dict):
        """
        Saves a record to the specified table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        columns = ", ".join(record.keys())
        placeholders = ", ".join(["?" for _ in record])
        values = list(record.values())

        cursor.execute(
            f"INSERT INTO {collection} ({columns}) VALUES ({placeholders})",
            values
        )

        conn.commit()
        conn.close()

    def update(self, collection: str, updates: dict, audit_id: str):
        """
        Updates fields in a record matching audit_id.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [audit_id]

        cursor.execute(
            f"UPDATE {collection} SET {set_clause} WHERE audit_id = ?",
            values
        )

        conn.commit()
        conn.close()

    def get_all(self, collection: str, audit_id: str = None) -> list:
        """
        Fetches all records from a table.
        Optionally filtered by audit_id.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if audit_id:
            cursor.execute(
                f"SELECT * FROM {collection} WHERE audit_id = ?",
                [audit_id]
            )
        else:
            cursor.execute(f"SELECT * FROM {collection}")

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def get_latest_audit_id(self) -> str:
        """
        Returns the most recent audit_id from audit_logs.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT audit_id FROM audit_logs ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None