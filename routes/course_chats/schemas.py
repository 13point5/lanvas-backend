from pydantic import BaseModel


class CourseChat(BaseModel):
    id: int
    title: str
    course_id: int
    member_id: int
    created_at: str


class CourseChatCreateRequest(BaseModel):
    title: str


class CourseChatUpdateRequest(BaseModel):
    title: str


class ChatRequest(BaseModel):
    chat_id: int | None
    message: str
