from supabase import Client
from typing import List

from routes.course_chat_topics.schemas import CourseChatTopic

TABLE_NAME = "course_chat_topics"


def create_course_chat_topic(
    db: Client, course_id: int, name: str
) -> CourseChatTopic:
    res = (
        db.table(TABLE_NAME)
        .insert({"course_id": course_id, "name": name})
        .execute()
        .data
    )
    return CourseChatTopic(**res[0])


def get_course_chat_topics(db: Client, course_id: int) -> List[CourseChatTopic]:
    res = (
        db.table(TABLE_NAME)
        .select("*")
        .eq("course_id", course_id)
        .execute()
        .data
    )
    return [CourseChatTopic(**x) for x in res]
