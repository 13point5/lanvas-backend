import setup
import os
from celery import Celery

from db.supabase import create_supabase_client

from routes.course_chat_topics.services import (
    get_course_chat_topics,
    create_course_chat_topics,
    increment_course_chat_topics_count,
)
from routes.course_chat_misconceptions.services import (
    get_course_chat_misconceptions,
    create_course_chat_misconceptions,
    increment_course_chat_misconceptions_count,
)

from analysis.topics import extract_topics, extract_new_and_old_topics
from analysis.misconceptions import (
    extract_misconceptions,
    extract_new_and_old_misconceptions,
)

celery = Celery("tasks", broker=os.environ.get("CELERY_BROKER_URL"))

db = create_supabase_client()


@celery.task(name="update_course_chat_topics_from_message")
def update_course_chat_topics_from_message(course_id: int, message: str):
    # Get existing topics discussed in the course
    existing_topics = get_course_chat_topics(db=db, course_id=course_id)

    # Get topics discussed in message
    message_topics = extract_topics(message=message)

    # Get new and old topics in the message
    topics = extract_new_and_old_topics(
        existing_topics=existing_topics, new_topics=message_topics
    )

    # Add new topics
    create_course_chat_topics(
        db=db, course_id=course_id, topics=topics.new_topics
    )

    # Increment count for existing topics
    increment_course_chat_topics_count(
        db=db, course_id=course_id, topic_ids=topics.used_topic_ids
    )


@celery.task(name="update_course_chat_misconceptions_from_message")
def update_course_chat_conceptionsfrom_message(course_id: int, message: str):
    # Get existing misconceptions found in the course
    existing_misconceptions = get_course_chat_misconceptions(
        db=db, course_id=course_id
    )

    # Get misconceptions discussed in message
    message_misconceptions = extract_misconceptions(message=message)

    # Get new and old misconceptions in the message
    misconceptions = extract_new_and_old_misconceptions(
        existing_misconceptions=existing_misconceptions,
        new_misconceptions=message_misconceptions,
    )

    # Add new misconceptions
    create_course_chat_misconceptions(
        db=db,
        course_id=course_id,
        misconceptions=misconceptions.new_misconceptions,
    )

    # Increment count for existing misconceptions
    increment_course_chat_misconceptions_count(
        db=db,
        course_id=course_id,
        misconception_ids=misconceptions.used_misconception_ids,
    )
