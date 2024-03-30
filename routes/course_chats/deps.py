from fastapi import Depends, HTTPException

from routes.course.deps import validate_course_membership
import routes.course_chats.services as CourseChatService

from db.supabase import create_supabase_client


def validate_chat_membership(chat_id: int, member=Depends(validate_course_membership)):
    db = create_supabase_client()

    chat = CourseChatService.get_course_chat(db=db, chat_id=chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat Not Found")

    if chat.member_id != member.id:
        raise HTTPException(status_code=403, detail="You don't have access to this chat")

    return chat
