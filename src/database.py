import os
import traceback
from datetime import datetime, timezone
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extensions import cursor
from psycopg2.extras import RealDictCursor
from psycopg2.sql import Identifier


class DatabaseManager:
    def __init__(self):
        self._conn = None

    def connect(self):
        load_dotenv()
        self._conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )

    @property
    def conn(self) -> psycopg2.extensions.connection:
        """接続オブジェクトを安全に取得するためのプロパティ。

        未接続（None）の場合はエラーを投げ、型チェッカーに「絶対に None を返さない」ことを伝えます。
        """
        if self._conn is None:
            raise RuntimeError(
                "データベースに接続されていません。事前に connect() を呼び出してください。"
            )
        return self._conn

    def fetch_all(self, query: str) -> list[dict]:
        # データの取得
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            results = cur.fetchall()
            return [dict(row) for row in results]

    def insert(self, table: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            # データの取得
            columns = data.keys()
            values = tuple(data.values())

            query = sql.SQL(
                "INSERT INTO {table} ({fields}) VALUES ({placeholders}) RETURNING *;"
            ).format(
                table=self.__create_table_indentifier(table),
                fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(", ").join([sql.Placeholder()] * len(values)),
            )

            with self.conn.cursor() as cur:
                cur.execute(query, values)
                results = self.__fetch_all_as_dict(cur)

            # 変更を保存（コミット）
            self.conn.commit()

            return results
        except Exception:
            traceback.print_exc()
            self.conn.rollback()
            return []

    def update(
        self, table: str, data: dict[str, Any], condition: dict[str, Any]
    ) -> list[dict[str, Any]]:
        try:
            update_data_all = data | {"updated_at": datetime.now(tz=timezone.utc)}
            condition_clause = sql.SQL("")
            if condition:
                condition_clause = self.__create_condition_clause(condition)

            query = sql.SQL(
                "UPDATE {table} SET {update_clause} {condition_clause} RETURNING *;"
            ).format(
                table=self.__create_table_indentifier(table),
                update_clause=self.__create_update_clause(update_data_all),
                condition_clause=condition_clause,
            )

            with self.conn.cursor() as cur:
                cur.execute(
                    query, tuple(update_data_all.values()) + tuple(condition.values())
                )
                results = self.__fetch_all_as_dict(cur)

            # 変更を保存（コミット）
            self.conn.commit()

            return results
        except Exception:
            traceback.print_exc()
            self.conn.rollback()
            return []

    def __create_update_clause(self, data: dict[str, Any]) -> sql.Composed:
        condition_querys = [
            sql.SQL("{}={}").format(sql.Identifier(k), sql.Placeholder()) for k in data
        ]

        return sql.SQL(", ").join(condition_querys)

    def delete(self, table: str, condition: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            condition_clause = sql.SQL("")
            if condition:
                condition_clause = self.__create_condition_clause(condition)
            # 結果の取得
            query = sql.SQL(
                "DELETE FROM {table} {where_clause} {condition_clause} RETURNING *;"
            ).format(
                table=self.__create_table_indentifier(table),
                condition_clause=condition_clause,
            )

            with self.conn.cursor() as cur:
                cur.execute(query, tuple(condition.values()))
                results = self.__fetch_all_as_dict(cur)

            # 変更を保存（コミット）
            self.conn.commit()

            return results
        except Exception:
            traceback.print_exc()
            self.conn.rollback()
            return []

    def __create_condition_clause(self, condition: dict[str, Any]) -> sql.Composed:
        condition_querys = [
            sql.SQL("{}={}").format(sql.Identifier(k), sql.Placeholder())
            for k in condition
        ]

        return sql.Composed([sql.SQL("WHERE"), sql.SQL(" AND ").join(condition_querys)])

    def __create_table_indentifier(self, table: str) -> Identifier:
        if "." in table:
            schema_name, table_name = table.split(".", 1)
            return sql.Identifier(schema_name, table_name)

        return sql.Identifier(table)

    def __fetch_all_as_dict(self, cur: cursor) -> list[dict[str, Any]]:
        records = cur.fetchall()
        columns = [desc[0] for desc in cur.description or []]

        fields: list[dict[str, Any]] = []
        for row in records:
            row_data = {}
            for column, value in zip(columns, row):
                row_data[column] = value
            fields.append(row_data)
        return fields
