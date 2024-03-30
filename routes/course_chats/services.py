from typing import Optional

from supabase import Client

from routes.course_chats.schemas import CourseChat, CourseChatCreateRequest, CourseChatUpdateRequest

TABLE_NAME = "course_chats"


def get_course_chats(db: Client, course_id: int, member_id: int) -> list[CourseChat]:
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).eq("member_id", member_id).execute().data
    return [CourseChat(**x) for x in res]


def get_course_chat(db: Client, chat_id: int) -> Optional[CourseChat]:
    res = db.table(TABLE_NAME).select("*").eq("id", chat_id).execute().data
    if not res:
        return None
    return CourseChat(**res[0])


def create_course_chat(db: Client, course_id: int, data: CourseChatCreateRequest, member_id: int) -> CourseChat:
    res = db.table(TABLE_NAME).insert({"course_id": course_id, "title": data.title, "member_id": member_id}).execute().data
    return CourseChat(**res[0])


def update_course_chat(db: Client, chat_id: int, data: CourseChatUpdateRequest) -> CourseChat:
    res = db.table(TABLE_NAME).update(data.model_dump(exclude_unset=True)).eq("id", chat_id).execute().data
    return CourseChat(**res[0])


def delete_course_chat(db: Client, chat_id: int):
    res = db.table(TABLE_NAME).delete().eq("id", chat_id).execute().data
    return res
