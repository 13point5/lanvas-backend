from pydantic import BaseModel

from routes.course_members.schemas import CourseMemberRole


class Course(BaseModel):
    id: int
    title: str
    created_at: str


class CourseCreateRequest(BaseModel):
    title: str


class UserCourse(BaseModel):
    role: CourseMemberRole
    course: Course
