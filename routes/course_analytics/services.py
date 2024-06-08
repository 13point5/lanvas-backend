from supabase import Client
from typing import List

from routes.course_analytics.schemas import CourseChatTopic

TABLE_NAME = "course_chat_topics"


def create_course_chat_topics(
    db: Client, course_id: int, topics: List[str]
) -> List[CourseChatTopic]:
    res = (
        db.table(TABLE_NAME)
        .insert([{"course_id": course_id, "name": name} for name in topics])
        .execute()
        .data
    )
    return [CourseChatTopic(**x) for x in res]


def get_course_chat_topics(db: Client, course_id: int) -> List[CourseChatTopic]:
    res = (
        db.table(TABLE_NAME)
        .select("*")
        .eq("course_id", course_id)
        .execute()
        .data
    )
    return [CourseChatTopic(**x) for x in res]


def increment_course_chat_topics_count(
    db: Client, course_id: int, topic_ids: List[int]
) -> CourseChatTopic:
    res = (
        db.rpc(
            "increment_course_chat_topics",
            {"course_id": course_id, "topic_ids": topic_ids},
        )
        .execute()
        .data
    )
    return [CourseChatTopic(**x) for x in res]
