# app/infrastructure/database.py

from __future__ import annotations

import os
import sqlite3


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None

    def get_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            d = os.path.dirname(self.db_path)
            if d:
                os.makedirs(d, exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
        return self.connection

    @staticmethod
    def init_db(conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()

        # projects table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            dxf_file TEXT NOT NULL,
            description TEXT DEFAULT '',
            last_control TEXT DEFAULT ''
        )
        ''')

        # control_points table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS control_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL
                REFERENCES projects(id) ON DELETE CASCADE,
            number INTEGER NOT NULL,
            name TEXT NOT NULL,
            kind TEXT NOT NULL,
            true_value REAL NOT NULL,
            tol_plus REAL DEFAULT 0,
            tol_minus REAL DEFAULT 0,
            x REAL DEFAULT 0,
            y REAL DEFAULT 0,
            entity_handle TEXT DEFAULT '',
            measured_value REAL
        )
        ''')

        # history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL
                REFERENCES projects(id) ON DELETE CASCADE,
            timestamp TEXT NOT NULL,
            operator TEXT DEFAULT '',
            action TEXT NOT NULL,
            point_number INTEGER,
            old_value TEXT DEFAULT '',
            new_value TEXT DEFAULT ''
        )
        ''')

        conn.commit()

# Usage example
if __name__ == "__main__":
    db_path = 'data/otk.db'
    db = Database(db_path)
    init_db_connection = db.get_connection()
    Database.init_db(init_db_connection)
