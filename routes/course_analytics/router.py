from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_chat_topics.services as CourseChatTopicsService
import routes.course_chat_misconceptions.services as CourseChatMisconceptionsService

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/analytics",
    tags=["analytics"],
    dependencies=[
        Depends(AuthBearer()),
        Depends(CourseDeps.validate_course_membership),
    ],
)


@router.get("/topics")
def get_course_chat_topics(course_id: int):
    return CourseChatTopicsService.get_course_chat_topics(
        db=db, course_id=course_id
    )


@router.get("/topics")
def get_course_chat_misconceptions(course_id: int):
    return CourseChatMisconceptionsService.get_course_chat_misconceptions(
        db=db, course_id=course_id
    )
