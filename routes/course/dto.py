from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MessageRole(str, Enum):
    human = "human"
    assistant = "assistant"


class ChatMessage(BaseModel):
    content: str
    role: MessageRole


class CourseChatRequest(BaseModel):
    # folder_id: int | None = None
    message: str
    # history: list[ChatMessage]
