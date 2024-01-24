from pydantic import BaseModel


class Course(BaseModel):
    id: int
    title: str
    created_at: str


class CourseCreateRequest(BaseModel):
    title: str
