from typing import Optional

from supabase import Client

from routes.course.schemas import Course

TABLE_NAME = "courses"


def get_course(db: Client, course_id: int) -> Optional[Course]:
    res = db.table(TABLE_NAME).select("*").eq("id", course_id).execute().data

    if len(res) < 1:
        return None

    return Course(**res[0])


def create_course(db: Client, title: str) -> Course:
    res = db.table(TABLE_NAME).insert({"title": title}).execute().data

    return Course(**res[0])
