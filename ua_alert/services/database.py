import sqlite3
from pathlib import Path

class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, event_key TEXT UNIQUE NOT NULL, region TEXT NOT NULL,
          previous_status TEXT NOT NULL, new_status TEXT NOT NULL, threat_category TEXT NOT NULL,
          started_at TEXT, ended_at TEXT, source TEXT NOT NULL, created_at TEXT NOT NULL);
        """)
        self.conn.commit()

    def get(self, key, default=""):
        row = self.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default

    def set(self, key, value):
        self.conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))
        self.conn.commit()

    def record(self, event):
        self.conn.execute("INSERT OR IGNORE INTO events(event_key,region,previous_status,new_status,threat_category,started_at,ended_at,source,created_at) VALUES(?,?,?,?,?,?,?,?,?)", event)
        self.conn.commit()

    def history(self, query=""):
        return self.conn.execute("SELECT * FROM events WHERE region LIKE ? OR threat_category LIKE ? ORDER BY id DESC LIMIT 1000", (f"%{query}%", f"%{query}%")).fetchall()

    def close(self): self.conn.close()
