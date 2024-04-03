from pydantic import BaseModel
from typing import Optional


class CourseChatMessage(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    metadata: Optional[dict]
    created_at: str


class CourseChatMessageCreateRequest(BaseModel):
    role: str
    content: str
    metadata: Optional[dict]
