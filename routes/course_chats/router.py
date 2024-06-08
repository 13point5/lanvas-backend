from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

from chains.rag import get_course_rag_chain

from analysis.topics import extract_new_topics

import routes.course.deps as CourseDeps
import routes.course_chats.deps as CourseChatDeps
import routes.course_chats.services as CourseChatService
from routes.course_chats.schemas import (
    CourseChat,
    CourseChatCreateRequest,
    CourseChatUpdateRequest,
    ChatRequest,
)

import routes.course_chat_messages.services as CourseChatMessageService
from routes.course_chat_messages.schemas import CourseChatMessageCreateRequest

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/chats",
    tags=["chats"],
    dependencies=[
        Depends(AuthBearer()),
        Depends(CourseDeps.validate_course_membership),
    ],
)


@router.get("/", response_model=list[CourseChat])
def get_course_chats(
    course_id: int, member=Depends(CourseDeps.validate_course_membership)
):
    return CourseChatService.get_course_chats(
        db=db, course_id=course_id, member_id=member.id
    )


@router.post("/", response_model=CourseChat)
def create_course_chat(
    course_id: int,
    body: CourseChatCreateRequest,
    member=Depends(CourseDeps.validate_course_membership),
):
    return CourseChatService.create_course_chat(
        db=db, course_id=course_id, data=body, member_id=member.id
    )


@router.patch(
    "/{chat_id}",
    response_model=CourseChat,
    dependencies=[Depends(CourseChatDeps.validate_chat_membership)],
)
def update_course_chat(chat_id: int, body: CourseChatUpdateRequest):
    return CourseChatService.update_course_chat(
        db=db, chat_id=chat_id, data=body
    )


@router.delete(
    "/{chat_id}",
    dependencies=[Depends(CourseChatDeps.validate_chat_membership)],
)
def delete_course_chat(chat_id: int):
    return CourseChatService.delete_course_chat(db=db, chat_id=chat_id)


@router.post("/chat")
def chat(
    course_id: int,
    body: ChatRequest,
    member=Depends(CourseDeps.validate_course_membership),
):
    message = body.message
    chat_id = body.chat_id

    if chat_id is None:
        chat = CourseChatService.create_course_chat(
            db=db,
            course_id=course_id,
            member_id=member.id,
            data=CourseChatCreateRequest(title=message[:30]),
        )
        chat_id = chat.id

    conversational_rag_chain = get_course_rag_chain(
        course_id=course_id, db_client=db
    )

    response = conversational_rag_chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": chat_id}},
    )

    return response
