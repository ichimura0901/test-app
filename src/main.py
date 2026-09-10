from datetime import datetime
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st


class TaskFrameColumn(Enum):
    LABEL = "タスク"
    PERIOD = "期限"
    STATUS = "ステータス"
    EDIT = "編集"
    DELETE = "削除"


ERROR_CSS = {
    "padding": "5px",
    "color": "red",
    "background-color": "#fff0f5",
    "height": "{height}px",
    "font-size": "13px",
    "align-items": "center",
    "radius": "3px",
}
REGISTER_BUTTON_STR = "登録"
EDIT_BUTTON_STR = "編集"
DELETE_BUTTON_STR = "削除"
JST_TZINFO = ZoneInfo("Asia/Tokyo")


def create_error_tag_frame():
    return '<div style="' + create_css_str(ERROR_CSS) + '">{text}</div>'


def create_css_str(css_dict: dict[str, str]):
    css_str = ""

    for key, value in css_dict.items():
        css_str += f"{key}:{value};"
    return css_str


class TaskStatus(Enum):
    PENDING = "未対応"
    INPROGRESS = "対応中"
    COMPLETE = "完了"


class TodoTask:
    def __init__(
        self,
        task_id: int | None,
        label: str,
        period: datetime | None,
        status: TaskStatus | None,
        note: str,
    ):
        self.task_id = task_id
        self.label = label
        self.period = period
        self.status = status
        self.note = note


def fetch_data() -> list[TodoTask]:
    """タスク一覧を取得

    Returns:
        list[TodoTask]: タスク一覧
    """
    task_1 = TodoTask(
        1,
        "個人目標の座学",
        datetime(2026, 10, 1, 15, 30, 0, tzinfo=JST_TZINFO),
        TaskStatus.INPROGRESS,
        "",
    )
    task_2 = TodoTask(
        2,
        "掃除",
        datetime(2026, 10, 2, 12, 45, 0, tzinfo=JST_TZINFO),
        TaskStatus.PENDING,
        "",
    )
    return [task_1, task_2]


def calculate_max_task_id(tasks: list[TodoTask], current_max_task_id: int = 1) -> int:
    """最大タスクIDを取得

    Args:
        tasks (list[TodoTask]): タスク一覧
        current_max_task_id (int): 現在の最大タスクID

    Returns:
        int: 最大タスクID
    """
    if not tasks:
        return 1

    return max([t.task_id for t in tasks if t.task_id] + [current_max_task_id])


def create_data_frame(tasks: list[TodoTask]) -> dict[str, list[Any]]:
    """データフレーム辞書作成

    Args:
        tasks (list[TodoTask]): タスク一覧

    Returns:
        dict[str, Any]: データフレーム辞書
    """
    data: dict[str, list[Any]] = {
        TaskFrameColumn.LABEL.value: [],
        TaskFrameColumn.PERIOD.value: [],
        TaskFrameColumn.STATUS.value: [],
        TaskFrameColumn.EDIT.value: [],
        TaskFrameColumn.DELETE.value: [],
    }
    for task in tasks:
        data[TaskFrameColumn.LABEL.value].append(task.label)
        data[TaskFrameColumn.PERIOD.value].append(
            task.period.strftime("%Y/%m/%d %H:%M") if task.period else ""
        )
        data[TaskFrameColumn.STATUS.value].append(
            task.status.value if task.status else ""
        )
        data[TaskFrameColumn.EDIT.value].append(
            EDIT_BUTTON_STR if task.task_id else REGISTER_BUTTON_STR
        )
        data[TaskFrameColumn.DELETE.value].append(DELETE_BUTTON_STR)

    return data


@st.dialog("編集")
def render_edit_dialog(tasks: list[TodoTask], row_index: int):
    """編集ダイアログ描画

    Args:
        tasks (list[TodoTask]): タスク一覧
        row_index (int): 行のインデックス
    """
    # 編集対象のダイアログを取得
    task = tasks[row_index]

    with st.form("detail_form"):
        label_error = st.empty()
        label = st.text_input("タスク名", value=task.label if task.label else "")
        date_column, time_column = st.columns([2, 1])

        period = task.period if task.period else datetime.now(JST_TZINFO)
        with date_column:
            input_date = st.date_input("期限", value=period.date())

        with time_column:
            input_time = st.time_input(
                "時刻",
                value=period.time(),
                label_visibility="hidden",
            )

        input_status = create_status_selectbox(task.status)

        input_note = st.text_area("メモ", value=task.note)

        update_button, cancel_button = st.columns(2)
        # 更新時のイベント
        with update_button:
            if st.form_submit_button(
                "更新" if task.task_id else REGISTER_BUTTON_STR, width="stretch"
            ):
                if not label:
                    label_error.write(
                        create_error_tag_frame().format(
                            text="タスク名は必須です", height=30
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    if not task.task_id:
                        task.task_id = (
                            calculate_max_task_id(
                                st.session_state.tasks, st.session_state.max_task_id
                            )
                            + 1
                        )
                        st.session_state.max_task_id = task.task_id

                    task.label = label
                    task.period = datetime.combine(
                        input_date, input_time, tzinfo=JST_TZINFO
                    )
                    task.status = input_status
                    task.note = input_note
                    st.rerun()

        # キャンセル時のイベント
        with cancel_button:
            if st.form_submit_button("キャンセル", width="stretch"):
                st.rerun()


@st.dialog("削除")
def render_delete_dialog(tasks: list[TodoTask], row_index: int):
    """削除ダイアログ描画

    Args:
        tasks (list[TodoTask]): タスク一覧
        row_index (int): 行のインデックス
    """
    with st.form("delete_form"):
        st.write("削除しますか？")

        ok_button, cancel_button = st.columns(2)
        # 削除時のイベント
        with ok_button:
            if st.form_submit_button("OK", width="stretch"):
                del tasks[row_index]
                st.rerun()

        # キャンセル時のイベント
        with cancel_button:
            if st.form_submit_button("キャンセル", width="stretch"):
                st.rerun()


def edit_action():
    """編集ボタン押下時のイベント"""
    click = st.session_state.edit_buttons
    render_edit_dialog(st.session_state.tasks, click["row"])


def delete_action():
    """削除ボタン押下時のイベント"""
    click = st.session_state.delete_buttons
    row_index = click["row"]
    if st.session_state.tasks[row_index].task_id:
        render_delete_dialog(st.session_state.tasks, row_index)
    else:
        del st.session_state.tasks[row_index]


def create_status_selectbox(status: TaskStatus | None) -> TaskStatus:
    """ステータスのプルダウン作成

    Args:
        status (TaskStatus | None): ステータス

    Returns:
        TaskStatus: 選択中のステータスの値
    """

    def render_status(status: TaskStatus | None):
        return status.value if status else None

    status_index = next(
        (i for i, s in enumerate(list(TaskStatus)) if s.value == render_status(status)),
        0,
    )
    input_status: TaskStatus = st.selectbox(
        "ステータス",
        options=list(TaskStatus),
        index=status_index,
        format_func=render_status,
    )

    return input_status


def render():
    """画面の描画"""
    st.title("TODOアプリ")
    _, col2 = st.columns([4, 1])
    with col2:
        if st.button("タスク追加", key="add_button", width="stretch", type="primary"):
            st.session_state.tasks.append(TodoTask(None, "", None, None, ""))

    st.dataframe(
        pd.DataFrame(create_data_frame(st.session_state.tasks)),
        column_config={
            TaskFrameColumn.EDIT.value: st.column_config.ButtonColumn(
                "",
                on_click=edit_action,
                key="edit_buttons",
            ),
            TaskFrameColumn.DELETE.value: st.column_config.ButtonColumn(
                "",
                on_click=delete_action,
                key="delete_buttons",
            ),
        },
        hide_index=True,
    )


def main():
    # データ取得
    if "tasks" not in st.session_state:
        st.session_state.tasks = fetch_data()
        st.session_state.max_task_id = calculate_max_task_id(st.session_state.tasks)

    # 画面描画
    render()


main()
