from pydantic import BaseModel
from typing import Optional


class CourseFolder(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    course_id: int
    created_at: str


class CourseFolderCreateRequest(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CourseFolderUpdateRequest(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
