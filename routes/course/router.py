import json
import os
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile

from .dto import (
    AddCourseMembers,
    CreateCourseFolderRequest,
    CreateCourseRequest,
    UpdateCourseFolderRequest,
    UpdateCourseMaterialRequest,
    CourseChatRequest,
)
from db.supabase import create_supabase_client
from db.vectorstore import get_similar_documents_from_files
from middlewares.auth import AuthBearer
from middlewares.auth.auth_bearer import get_current_user
from models.user_identity import UserIdentity

from parsers.pdf import process_pdf


supabase_client = create_supabase_client()

course_router = APIRouter(prefix="/courses", tags=["courses"])


@course_router.post("/{course_id}/chat", dependencies=[Depends(AuthBearer())])
def course_chat(course_id: int, body: CourseChatRequest):
    print("body", body)

    documents = get_similar_documents_from_files(query=body.message, file_ids=[23, 24])

    return documents


@course_router.get("/{course_id}", dependencies=[Depends(AuthBearer())])
def get_course(
    course_id: int,
    current_user: UserIdentity = Depends(get_current_user),
):
    res = (
        supabase_client.table("courses")
        .select("*, course_members(*), course_folders(*), course_materials(*)")
        .eq("id", course_id)
        .eq("course_members.course_id", course_id)
        .eq("course_folders.course_id", course_id)
        .eq("course_materials.course_id", course_id)
        .execute()
    )
    data = res.data

    if len(data) < 1:
        raise HTTPException(status_code=404, detail="Course not found")

    course = data[0]

    if (
        current_user.email
        not in next(filter(lambda x: x["email"] == current_user.email, course["course_members"]), None)["email"]
    ):
        raise HTTPException(status_code=403, detail="You don't have access to this course")

    return course


@course_router.post("/", dependencies=[Depends(AuthBearer())])
def create_course(
    body: CreateCourseRequest,
    current_user: UserIdentity = Depends(get_current_user),
):
    res = supabase_client.table("courses").insert({"title": body.title}).execute()
    course = res.data[0]

    supabase_client.table("course_members").insert(
        {"course_id": course["id"], "email": current_user.email, "role": "teacher"}
    ).execute()

    return {"course": course}


@course_router.post("/{course_id}/folder", dependencies=[Depends(AuthBearer())])
def create_folder(course_id: int, body: CreateCourseFolderRequest):
    res = (
        supabase_client.table("course_folders")
        .insert({"course_id": course_id, "name": body.name, "parent_id": body.parentId})
        .execute()
    )
    return res.data[0]


@course_router.patch("/{course_id}/folder/{folder_id}", dependencies=[Depends(AuthBearer())])
def update_folder(course_id: int, folder_id: int, body: UpdateCourseFolderRequest):
    if not any([field in UpdateCourseFolderRequest.model_fields.keys() for field in body.model_fields.keys()]):
        raise HTTPException(status_code=400, detail="No valid fields provided")

    if body.parent_id is not None and body.parent_id == folder_id:
        raise HTTPException(status_code=400, detail="Cannot set parent_id to self")

    update_query = {}
    for field, value in body.model_dump().items():
        if value is not None:
            update_query[field] = value

    res = supabase_client.table("course_folders").update(update_query).eq("id", folder_id).execute()
    return res.data[0]


@course_router.post("/{course_id}/members", dependencies=[Depends(AuthBearer())])
def add_course_members(course_id: int, body: AddCourseMembers):
    supabase_client.table("course_members").insert(
        [{"course_id": course_id, "email": member.email, "role": member.role} for member in body.members]
    ).execute()

    res = supabase_client.table("course_members").select("*").eq("course_id", course_id).execute()

    return res.data


def set_course_material_status(file_id: int, status: str):
    return supabase_client.table("course_materials").update({"status": status}).eq("id", file_id).execute()


file_processors = {
    ".pdf": process_pdf,
}


@course_router.post("/{course_id}/folder/{folder_id}/upload", dependencies=[Depends(AuthBearer())])
async def upload_file(course_id: int, folder_id: int, uploadFile: UploadFile):
    # check if file type is supported
    file_extension = os.path.splitext(uploadFile.filename)[-1]
    if file_extension not in file_processors:
        raise Exception(f"Unsupported file extension: {file_extension}")

    # add entry to course_materials table
    res = (
        supabase_client.table("course_materials")
        .insert({"course_id": course_id, "folder_id": folder_id, "status": "uploading", "name": uploadFile.filename})
        .execute()
    )
    file_id = res.data[0]["id"]

    # upload file to storage
    file_content = await uploadFile.read()
    file_path = str(course_id) + "/" + str(uploadFile.filename)

    try:
        supabase_client.storage.from_("course-materials").upload(path=file_path, file=file_content)
    except Exception as e:
        print(e)

        if "The resource already exists" in str(e):
            raise HTTPException(
                status_code=403,
                detail=f"File {uploadFile.filename} already exists in storage.",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to upload file to storage. {e}")

    # process file
    set_course_material_status(file_id=file_id, status="processing")
    loader_class = file_processors[file_extension]
    documents, embeddings = await loader_class(uploadFile, file_id)
    rows = [
        {
            "content": doc.page_content,
            "embedding": embeddings[index],
            "metadata": doc.metadata,
        }
        for index, doc in enumerate(documents)
    ]

    # store embeddings
    UPLOAD_BATCH_SIZE = 500
    for i in range(0, len(rows), UPLOAD_BATCH_SIZE):
        batch = rows[i : i + UPLOAD_BATCH_SIZE]
        supabase_client.table("documents").insert(batch).execute()

    # update course_materials status
    set_course_material_status(file_id=file_id, status="ready")

    # get latest course_materials data
    materialData = supabase_client.table("course_materials").select("*").eq("id", file_id).execute().data[0]

    return materialData


@course_router.patch("/{course_id}/material/{material_id}", dependencies=[Depends(AuthBearer())])
def update_material(course_id: int, material_id: int, body: UpdateCourseMaterialRequest):
    if not any([field in UpdateCourseMaterialRequest.model_fields.keys() for field in body.model_fields.keys()]):
        raise HTTPException(status_code=400, detail="No valid fields provided")

    update_query = {}
    for field, value in body.model_dump().items():
        if value is not None:
            update_query[field] = value

    res = supabase_client.table("course_materials").update(update_query).eq("id", material_id).execute()
    return res.data[0]
