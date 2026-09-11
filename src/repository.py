from typing import Any

from database import DatabaseManager


def get_task(client: DatabaseManager) -> list[dict]:
    """DatabaseManager

    Args:
        client (DatabaseManager): クライアント

    Returns:
        list[dict]: タスク一覧
    """
    return client.fetch_all("SELECT * FROM app_db.todo_task")


def insert_task(client: DatabaseManager, item: dict[str, Any]) -> None:
    """DatabaseManager

    Args:
        client (DatabaseManager): クライアント
        item (dict[str, Any]): 項目

    Returns:
        list[dict]: タスク一覧
    """
    client.insert("app_db.task", item)
