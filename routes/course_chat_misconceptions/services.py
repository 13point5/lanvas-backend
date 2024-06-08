from supabase import Client
from typing import List

from routes.course_chat_misconceptions.schemas import CourseChatMisconception

TABLE_NAME = "course_chat_misconceptions"


def create_course_chat_misconceptions(
    db: Client, course_id: int, misconceptions: List[str]
) -> List[CourseChatMisconception]:
    res = (
        db.table(TABLE_NAME)
        .insert(
            [{"course_id": course_id, "name": name} for name in misconceptions]
        )
        .execute()
        .data
    )
    return [CourseChatMisconception(**x) for x in res]


def get_course_chat_misconceptions(
    db: Client, course_id: int
) -> List[CourseChatMisconception]:
    res = (
        db.table(TABLE_NAME)
        .select("*")
        .eq("course_id", course_id)
        .execute()
        .data
    )
    return [CourseChatMisconception(**x) for x in res]


def increment_course_chat_misconceptions_count(
    db: Client, course_id: int, misconception_ids: List[int]
) -> List[CourseChatMisconception]:
    res = (
        db.rpc(
            "increment_course_chat_misconceptions",
            {"course_id": course_id, "misconception_ids": misconception_ids},
        )
        .execute()
        .data
    )
    return [CourseChatMisconception(**x) for x in res]
