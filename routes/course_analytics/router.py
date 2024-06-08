from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_analytics.services as CourseAnalyticsService

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
    return CourseAnalyticsService.get_course_chat_topics(
        db=db, course_id=course_id
    )
