import setup
import os
from celery import Celery

from db.supabase import create_supabase_client

from routes.course_chat_topics.services import (
    get_course_chat_topics,
    create_course_chat_topics,
)

from analysis.topics import extract_topics, extract_new_topics

celery = Celery("tasks", broker=os.environ.get("CELERY_BROKER_URL"))

db = create_supabase_client()


@celery.task(name="update_course_chat_topics_from_message")
def update_course_chat_topics_from_message(course_id: int, message: str):
    existing_topics = get_course_chat_topics(db=db, course_id=course_id)

    new_topics = extract_topics(message=message)

    new_unique_topics = extract_new_topics(
        existing_topics=existing_topics, new_topics=new_topics
    )

    new_course_chat_topics = create_course_chat_topics(
        db=db, course_id=course_id, topics=new_unique_topics
    )

    print("New uniq topics", new_course_chat_topics)

    pass
