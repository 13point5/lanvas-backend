from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_chats.deps as CourseChatDeps
import routes.course_chats.services as CourseChatService
from routes.course_chats.schemas import CourseChat, CourseChatCreateRequest, CourseChatUpdateRequest

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/chats",
    tags=["chats"],
    dependencies=[Depends(AuthBearer()), Depends(CourseDeps.validate_course_membership)],
)


@router.get("/", response_model=list[CourseChat])
def get_course_chat(course_id: int):
    return CourseChatService.get_course_chats(db=db, course_id=course_id)


@router.post("/", response_model=CourseChat)
def create_course_chat(course_id: int, body: CourseChatCreateRequest, member=Depends(CourseDeps.validate_course_membership)):
    return CourseChatService.create_course_chat(db=db, course_id=course_id, data=body, member_id=member.id)


@router.patch("/{chat_id}", response_model=CourseChat, dependencies=[Depends(CourseChatDeps.validate_chat_membership)])
def update_course_chat(chat_id: int, body: CourseChatUpdateRequest):
    return CourseChatService.update_course_chat(db=db, chat_id=chat_id, data=body)


@router.delete("/{chat_id}", dependencies=[Depends(CourseChatDeps.validate_chat_membership)])
def delete_course_chat(chat_id: int):
    return CourseChatService.delete_course_chat(db=db, chat_id=chat_id)
