from typing import Optional
from fastapi import UploadFile, HTTPException
from supabase import Client

from routes.course_materials.schemas import CourseMaterial, CourseMaterialUpdateRequest
from routes.course_materials.constants import CourseMaterialStatus, STORAGE_BUCKET

TABLE_NAME = "course_materials"


def get_course_materials(db: Client, course_id: int) -> list[CourseMaterial]:
    res = db.table(TABLE_NAME).select("*").eq("course_id", course_id).execute().data
    return [CourseMaterial(**x) for x in res]


def get_course_material(db: Client, material_id: int) -> Optional[CourseMaterial]:
    res = db.table(TABLE_NAME).select("*").eq("id", material_id).execute().data
    if len(res) == 0:
        return None
    return CourseMaterial(**res[0])


def update_course_material(db: Client, material_id: int, data: CourseMaterialUpdateRequest) -> CourseMaterial:
    res = db.table(TABLE_NAME).update(data.model_dump(exclude_unset=True)).eq("id", material_id).execute().data
    return CourseMaterial(**res[0])


def create_course_material(
    db: Client, course_id: int, folder_id: Optional[int], name: str, status: CourseMaterialStatus = CourseMaterialStatus.uploading
) -> CourseMaterial:
    res = (
        db.table(TABLE_NAME)
        .insert({"course_id": course_id, "folder_id": folder_id, "name": name, "status": status})
        .execute()
        .data
    )
    return CourseMaterial(**res[0])


def update_course_material_status(db: Client, material_id: int, status: CourseMaterialStatus) -> CourseMaterial:
    res = db.table(TABLE_NAME).update({"status": status}).eq("id", material_id).execute().data
    return CourseMaterial(**res[0])


async def upload_course_material_to_storage(db: Client, course_id: int, file_data: UploadFile):
    file_content = await file_data.read()
    file_path = str(course_id) + "/" + str(file_data.filename)

    try:
        db.storage.from_(STORAGE_BUCKET).upload(path=file_path, file=file_content)
    except Exception as e:
        print(e)

        if "The resource already exists" in str(e):
            raise HTTPException(
                status_code=403,
                detail=f"File {file_data.filename} already exists in storage.",
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to upload file to storage. {e}")


def store_embeddings_by_batch(db: Client, rows, UPLOAD_BATCH_SIZE=500):
    for i in range(0, len(rows), UPLOAD_BATCH_SIZE):
        batch = rows[i : i + UPLOAD_BATCH_SIZE]
        db.table("documents").insert(batch).execute()
