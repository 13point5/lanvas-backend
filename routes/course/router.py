from fastapi import APIRouter, Depends

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# from langchain_core.output_parsers import StrOutputParser
from langchain.chains.combine_documents import create_stuff_documents_chain

# from prompts.chat import CHAT_PROMPT_TEMPLATE
from .dto import (
    CourseChatRequest,
)
from db.supabase import create_supabase_client
from db.vectorstore import get_similar_documents_from_files

from middlewares.auth import AuthBearer
from middlewares.auth.auth_bearer import get_current_user

from models.user_identity import UserIdentity

from routes.course.schemas import Course, CourseCreateRequest, UserCourse
from routes.course_members.schemas import CourseMemberRole, CourseMemberRequestItem

from . import deps

import routes.course.services as CourseService
import routes.course_members.services as CourseMemberService

from routes.course_members.router import router as course_members_router
from routes.course_folders.router import router as course_folders_router
from routes.course_materials.router import router as course_materials_router


db = create_supabase_client()

router = APIRouter(prefix="/courses", tags=["courses"], dependencies=[Depends(AuthBearer())])

router.include_router(course_members_router)
router.include_router(course_folders_router)
router.include_router(course_materials_router)


@router.get("/{course_id}", response_model=UserCourse)
def get_user_course(user_course: UserCourse = Depends(deps.get_user_course)):
    return user_course


@router.post("/", response_model=Course)
def create_course(
    body: CourseCreateRequest,
    user: UserIdentity = Depends(get_current_user),
):
    course = CourseService.create_course(db=db, title=body.title)

    CourseMemberService.add_course_members(
        db=db,
        course_id=course.id,
        members=[CourseMemberRequestItem(email=user.email, role=CourseMemberRole.teacher)],
    )

    return course


@router.get("/", response_model=list[UserCourse])
def get_user_courses(
    user: UserIdentity = Depends(get_current_user),
):
    return CourseService.get_user_courses(db=db, user_email=user.email)


@router.post("/{course_id}/chat", dependencies=[Depends(deps.validate_course_membership)])
def course_chat(course_id: int, body: CourseChatRequest):
    print("body", body)

    documents = get_similar_documents_from_files(query=body.message, file_ids=[23, 24], match_count=2)

    llm = ChatOpenAI()

    prompt = ChatPromptTemplate.from_template(
        """Answer the following question based only on the provided context:

    <context>
    {context}
    </context>

    Question: {input}"""
    )

    document_chain = create_stuff_documents_chain(llm, prompt)

    output = document_chain.invoke({"input": body.message, "context": documents})

    return {"output": output, "documents": documents}
