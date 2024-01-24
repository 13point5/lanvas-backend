from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_folders.services as CourseFolderService
from routes.course_folders.schemas import CourseFolder, CourseFolderCreateRequest, CourseFolderUpdateRequest

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/folders",
    tags=["folders"],
    dependencies=[Depends(AuthBearer()), Depends(CourseDeps.validate_course_membership)],
)


@router.get("/", response_model=list[CourseFolder])
def get_course_folders(course_id: int):
    return CourseFolderService.get_course_folders(db=db, course_id=course_id)


@router.post("/", response_model=CourseFolder)
def create_course_folder(course_id: int, body: CourseFolderCreateRequest):
    return CourseFolderService.create_course_folder(db=db, course_id=course_id, data=body)


@router.patch("/{folder_id}", response_model=CourseFolder)
def update_course_folder(folder_id: int, body: CourseFolderUpdateRequest):
    return CourseFolderService.update_course_folder(db=db, folder_id=folder_id, data=body)
