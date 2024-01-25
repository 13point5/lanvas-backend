from typing import Optional

from supabase import Client

from routes.course.schemas import Course, UserCourse

import routes.course_members.services as CourseMemberService

TABLE_NAME = "courses"


def get_course(db: Client, course_id: int) -> Optional[Course]:
    res = db.table(TABLE_NAME).select("*").eq("id", course_id).execute().data

    if len(res) < 1:
        return None

    return Course(**res[0])


def create_course(db: Client, title: str) -> Course:
    res = db.table(TABLE_NAME).insert({"title": title}).execute().data

    return Course(**res[0])


def get_user_courses(db: Client, user_email: str) -> list[UserCourse]:
    res = db.table(CourseMemberService.TABLE_NAME).select("role, courses(*)").eq("email", user_email).execute().data
    return [UserCourse(course=item["courses"], role=item["role"]) for item in res]
