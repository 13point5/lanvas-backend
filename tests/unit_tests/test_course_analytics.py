import setup

from db.supabase import create_supabase_client

from routes.course_analytics.services import increment_course_chat_topics_count

db = create_supabase_client()


def test_increment_topic_count():
    res = increment_course_chat_topics_count(
        db=db, course_id=20, topic_ids=[1, 2]
    )
    print("res", res)
