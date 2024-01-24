from typing import Optional

from supabase import Client

from routes.course_folders.schemas import CourseFolder, CourseFolderCreateRequest, CourseFolderUpdateRequest

TABLE_NAME = "course_folders"


def get_course_folders(db: Client, course_id: int) -> list[CourseFolder]:
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).execute().data
    return [CourseFolder(**x) for x in res]


def create_course_folder(db: Client, course_id: int, data: CourseFolderCreateRequest) -> CourseFolder:
    res = db.table(TABLE_NAME).insert({"course_id": course_id, "name": data.name, "parent_id": data.parent_id}).execute().data
    return CourseFolder(**res[0])


def update_course_folder(db: Client, folder_id: int, data: CourseFolderUpdateRequest):
    res = db.table(TABLE_NAME).update(data.model_dump(exclude_unset=True)).eq("id", folder_id).execute().data
    return CourseFolder(**res[0])
