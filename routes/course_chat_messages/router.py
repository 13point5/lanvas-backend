from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_chats.deps as CourseChatDeps
import routes.course_chat_messages.services as CourseChatMessageService
from routes.course_chat_messages.schemas import CourseChatMessage, CourseChatMessageCreateRequest

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/chats/{chat_id}/messages",
    tags=["messages"],
    dependencies=[
        Depends(AuthBearer()),
        Depends(CourseDeps.validate_course_membership),
        Depends(CourseChatDeps.validate_chat_membership),
    ],
)


@router.get("/")
def get_chat_messages(chat_id: int):
    return CourseChatMessageService.get_chat_messages(db=db, chat_id=chat_id)


@router.post("/")
def create_chat_message(chat_id: int, body: CourseChatMessageCreateRequest):
    return CourseChatMessageService.create_chat_message(db=db, chat_id=chat_id, data=body)
