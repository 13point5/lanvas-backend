from fastapi import Depends, HTTPException

from middlewares.auth.auth_bearer import get_current_user

from models.user_identity import UserIdentity

import routes.course.services as CourseService
import routes.course_members.services as CourseMemberService

from db.supabase import create_supabase_client


def validate_course_membership(course_id: int, current_user: UserIdentity = Depends(get_current_user)):
    db = create_supabase_client()

    member = CourseMemberService.get_course_member_by_email(db=db, course_id=course_id, email=current_user.email)

    if not member:
        raise HTTPException(status_code=403, detail="You don't have access to this course")

    return member


def get_course(course_id: int, _=Depends(validate_course_membership)):
    db = create_supabase_client()

    course = CourseService.get_course(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course Not Found")

    return course
