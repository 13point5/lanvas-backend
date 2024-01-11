from enum import Enum
from typing import Optional
from pydantic import BaseModel


class CreateCourseRequest(BaseModel):
    title: str


class CreateCourseFolderRequest(BaseModel):
    name: str
    parentId: int | None = None


class UpdateCourseFolderRequest(BaseModel):
    name: str | None = None
    parent_id: int | None = None


class CourseMember(BaseModel):
    email: str
    role: str


class AddCourseMembers(BaseModel):
    members: list[CourseMember]


class UpdateCourseMaterialRequest(BaseModel):
    name: str | None = None
    folder_id: int | None = None


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
