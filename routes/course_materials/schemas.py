from pydantic import BaseModel
from typing import Optional


class CourseMaterial(BaseModel):
    id: int
    name: str
    folder_id: Optional[int]
    course_id: int
    status: str
    created_at: str


class CourseMaterialUpdateRequest(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[int] = None
