from enum import Enum
from pydantic import BaseModel
from typing import Type


class CourseMemberRole(str, Enum):
    teacher = "teacher"
    student = "student"


class CourseMember(BaseModel):
    id: int
    email: str
    role: CourseMemberRole
    course_id: int
    created_at: str


class CourseMemberRequestItem(BaseModel):
    email: str
    role: CourseMemberRole


class CourseMembersAddRequest(BaseModel):
    members: list[CourseMemberRequestItem]
