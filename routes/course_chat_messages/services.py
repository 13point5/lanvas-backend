from typing import Optional

from supabase import Client

from routes.course_chat_messages.schemas import CourseChatMessage, CourseChatMessageCreateRequest

TABLE_NAME = "course_chat_messages"


def get_chat_messages(db: Client, chat_id: int) -> list[CourseChatMessage]:
    res = db.table(TABLE_NAME).select("*").eq("chat_id", chat_id).execute().data
    return [CourseChatMessage(**x) for x in res]


def create_chat_message(db: Client, chat_id: int, data: CourseChatMessageCreateRequest) -> CourseChatMessage:
    res = db.table(TABLE_NAME).insert({"chat_id": chat_id, **data.model_dump(exclude_unset=True)}).execute().data
    return CourseChatMessage(**res[0])


def delete_chat_message(db: Client, message_id: int):
    res = db.table(TABLE_NAME).delete().eq("id", message_id).execute().data
    return res
