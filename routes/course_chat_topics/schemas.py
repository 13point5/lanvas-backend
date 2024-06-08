from pydantic import BaseModel


class CourseChatTopic(BaseModel):
    id: int
    name: str
    count: int
    course_id: int
    created_at: str
