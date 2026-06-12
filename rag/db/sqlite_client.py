import sqlite3
from pathlib import Path
from rag.config import SQLITE_DB_PATH

def execute_querty(query: str):
    with sqlite3.connect(SQLITE_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        headers = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(headers, row)) for row in rows]



# print(execute_querty("SELECT * FROM claims"))
