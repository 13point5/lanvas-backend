from fastapi import HTTPException
from supabase import Client

TABLE_NAME = "course_materials"


def get_course_materials(db: Client, course_id: int):
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).execute().data
    return res
