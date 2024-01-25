import setup
import routes.course.services as CourseService

from db.supabase import create_supabase_client

db = create_supabase_client()

courses = CourseService.get_user_courses(db=db, user_email="test@gmail.com")
print(courses)
