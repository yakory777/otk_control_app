# app/infrastructure/sqlite_repository.py

import sqlite3
from typing import List, Optional
from app.domain.models import Project, ControlPoint

class SqliteProjectRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def list_all(self) -> List[Project]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects')
        rows = cursor.fetchall()
        return [Project(id=row[0], name=row[1], dxf_file=row[2], description=row[3], last_control=row[4]) for row in rows]

    def get_by_id(self, project_id: int) -> Optional[Project]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        if row:
            return Project(id=row[0], name=row[1], dxf_file=row[2], description=row[3], last_control=row[4])
        return None

    def add(self, project: Project):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO projects (name, dxf_file, description, last_control) VALUES (?, ?, ?, ?)',
                       (project.name, project.dxf_file, project.description, project.last_control))
        conn.commit()

    def update(self, project: Project):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE projects SET name = ?, dxf_file = ?, description = ?, last_control = ? WHERE id = ?',
                       (project.name, project.dxf_file, project.description, project.last_control, project.id))
        conn.commit()

    def remove(self, project_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()

    def next_id(self) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT IFNULL(MAX(id), 0) + 1 FROM projects')
        return cursor.fetchone()[0]

# Example usage
if __name__ == "__main__":
    db_path = 'data/otk.db'
    repo = SqliteProjectRepository(db_path)
    new_project = Project(name="Test Project", dxf_file="path/to/test.dxf")
    repo.add(new_project)