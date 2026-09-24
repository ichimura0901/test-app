from typing import Any

from database import DatabaseManager


def get_task(client: DatabaseManager) -> list[dict[str, Any]]:
    """DatabaseManager

    Args:
        client (DatabaseManager): クライアント

    Returns:
        list[dict]: タスク一覧
    """
    return client.fetch_all("SELECT * FROM app_db.todo_task ORDER BY id")


def insert_task(client: DatabaseManager, item: dict[str, Any]) -> list[dict[str, Any]]:
    """タスクの追加

    Args:
        client (DatabaseManager): クライアント
        item (dict[str, Any]): 項目

    Returns:
        list[dict[str, Any]]: タスク一覧
    """

    insert_item = {
        "id": item["task_id"],
        "label": item["label"],
        "period": item["period"],
        "status": item["status"],
        "note": item["note"],
    }
    return client.insert("app_db.todo_task", insert_item)


def update_task(
    client: DatabaseManager, item: dict[str, Any], task_id: int
) -> list[dict[str, Any]]:
    """タスクの追加

    Args:
        client (DatabaseManager): クライアント
        item (dict[str, Any]): 項目
        task_id (int): タスクID

    Returns:
        list[dict[str, Any]]: タスク一覧
    """

    update_item = {
        "label": item["label"],
        "period": item["period"],
        "status": item["status"],
        "note": item["note"],
    }
    return client.update("app_db.todo_task", update_item, {"id": task_id})


def delete_task(client: DatabaseManager, task_id: int) -> list[dict[str, Any]]:
    """DatabaseManager

    Args:
        client (DatabaseManager): クライアント
        task_id (int): タスクID

    Returns:
        list[dict[str, Any]]: タスク一覧
    """

    condition = {"id": task_id}
    return client.delete("app_db.todo_task", condition)
