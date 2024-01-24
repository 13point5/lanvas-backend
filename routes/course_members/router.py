from fastapi import APIRouter, Depends

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_members.services as CourseMemberService
from routes.course_members.schemas import CourseMembersAddRequest, CourseMember

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/members",
    tags=["members"],
    dependencies=[Depends(AuthBearer()), Depends(CourseDeps.validate_course_membership)],
)


@router.get("/", response_model=list[CourseMember])
def get_course_members(course_id: int):
    return CourseMemberService.get_course_members(db=db, course_id=course_id)


@router.post("/", response_model=list[CourseMember])
def add_course_members(course_id: int, body: CourseMembersAddRequest):
    CourseMemberService.add_course_members(db=db, course_id=course_id, members=body.members)
    return CourseMemberService.get_course_members(db=db, course_id=course_id)
