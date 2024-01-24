from typing import Optional

from supabase import Client

from routes.course_members.schemas import CourseMember, CourseMemberRequestItem

TABLE_NAME = "course_members"


def get_course_members(db: Client, course_id: int) -> list[CourseMember]:
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).execute().data
    return [CourseMember(**x) for x in res]


def get_course_member_by_email(db: Client, course_id: int, email: str) -> Optional[CourseMember]:
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).eq("email", email).execute().data

    if len(res) < 1:
        return None

    return CourseMember(**res[0])


def add_course_members(db: Client, course_id: int, members: list[CourseMemberRequestItem]) -> list[CourseMember]:
    res = (
        db.table(TABLE_NAME)
        .insert([{"course_id": course_id, "email": member.email, "role": member.role} for member in members])
        .execute()
        .data
    )

    return [CourseMember(**x) for x in res]
