# app/infrastructure/sqlite_repository.py

import sqlite3
from typing import List, Optional
from app.domain.models import HistoryEntry

class SqliteHistoryRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def log(self, project_id: int, operator: str, action: str, point_number: Optional[int], old_value: Optional[str], new_value: Optional[str]):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO history (project_id, timestamp, operator, action, point_number, old_value, new_value) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (project_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), operator, action, point_number, old_value, new_value))
        conn.commit()

    def get_history(self, project_id: int) -> List[HistoryEntry]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM history WHERE project_id = ?', (project_id,))
        rows = cursor.fetchall()
        return [HistoryEntry(id=row[0], project_id=row[1], timestamp=row[2], operator=row[3], action=row[4], point_number=row[5], old_value=row[6], new_value=row[7]) for row in rows]

# Example usage
if __name__ == "__main__":
    db_path = 'data/otk.db'
    repo = SqliteHistoryRepository(db_path)
    repo.log(project_id=1, operator="User", action="Add point", point_number=20, old_value="", new_value="")