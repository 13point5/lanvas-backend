from fastapi import APIRouter, Depends

from db.supabase import create_supabase_client

from middlewares.auth import AuthBearer
from middlewares.auth.auth_bearer import get_current_user

from models.user_identity import UserIdentity

from routes.course.schemas import Course, CourseCreateRequest, UserCourse
from routes.course_members.schemas import (
    CourseMemberRole,
    CourseMemberRequestItem,
)

from . import deps

import routes.course.services as CourseService
import routes.course_members.services as CourseMemberService

from routes.course_members.router import router as course_members_router
from routes.course_folders.router import router as course_folders_router
from routes.course_materials.router import router as course_materials_router
from routes.course_chats.router import router as course_chats_router
from routes.course_chat_messages.router import (
    router as course_chat_messages_router,
)
from routes.course_analytics.router import router as course_analytics_router

db = create_supabase_client()

router = APIRouter(
    prefix="/courses", tags=["courses"], dependencies=[Depends(AuthBearer())]
)

router.include_router(course_members_router)
router.include_router(course_folders_router)
router.include_router(course_materials_router)
router.include_router(course_chats_router)
router.include_router(course_chat_messages_router)
router.include_router(course_analytics_router)


@router.get("/{course_id}", response_model=UserCourse)
def get_user_course(user_course: UserCourse = Depends(deps.get_user_course)):
    return user_course


@router.post("/", response_model=Course)
def create_course(
    body: CourseCreateRequest,
    user: UserIdentity = Depends(get_current_user),
):
    course = CourseService.create_course(db=db, title=body.title)

    CourseMemberService.add_course_members(
        db=db,
        course_id=course.id,
        members=[
            CourseMemberRequestItem(
                email=user.email, role=CourseMemberRole.teacher
            )
        ],
    )

    return course


@router.get("/", response_model=list[UserCourse])
def get_user_courses(
    user: UserIdentity = Depends(get_current_user),
):
    return CourseService.get_user_courses(db=db, user_email=user.email)
