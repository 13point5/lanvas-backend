from pydantic import BaseModel


class CourseChatMisconception(BaseModel):
    id: int
    name: str
    count: int
    course_id: int
    created_at: str
