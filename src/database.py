import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


class DatabaseManager:
    def __init__(self):
        self.conn = None

    def connect(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

    def fetch_all(self, query: str) -> list[dict]:
        # データの取得
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            results = cur.fetchall()
            return [dict(row) for row in results]

    def insert(self, table: str, data: dict[str, Any]) -> list[dict]:
        # データの取得
        fields = ", ".join(data.keys())
        data = tuple(data.values())
        self.conn.cursor().execute(
            f"INSERT INTO {table} ({fields}) VALUES ({'%s' * len(data)})", data
        )

        # 変更を保存（コミット）
        self.conn.commit()
