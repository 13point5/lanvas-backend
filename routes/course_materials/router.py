from fastapi import APIRouter, Depends, UploadFile, HTTPException, Form
from typing import Annotated

from middlewares.auth import AuthBearer

from db.supabase import create_supabase_client

import routes.course.deps as CourseDeps
import routes.course_materials.services as CourseMaterialService
import routes.course_materials.utils as CourseMaterialUtils
from routes.course_materials.constants import CourseMaterialStatus
from routes.course_materials.schemas import CourseMaterial, CourseMaterialUpdateRequest

db = create_supabase_client()

router = APIRouter(
    prefix="/{course_id}/materials",
    tags=["materials"],
    dependencies=[Depends(AuthBearer()), Depends(CourseDeps.validate_course_membership)],
)


@router.get("/", response_model=list[CourseMaterial])
def get_course_materials(course_id: int):
    return CourseMaterialService.get_course_materials(db=db, course_id=course_id)


@router.patch("/{material_id}", response_model=CourseMaterial)
def update_course_material(material_id: int, body: CourseMaterialUpdateRequest):
    return CourseMaterialService.update_course_material(db=db, material_id=material_id, data=body)


@router.post("/upload")
async def upload_course_material(course_id: int, folder_id: Annotated[int, Form()], uploadFile: UploadFile) -> CourseMaterial:
    print("folder_id", folder_id)
    # check if file type is supported
    if not CourseMaterialUtils.is_file_type_supported(file_data=uploadFile):
        raise HTTPException(status_code=400, detail="File type not supported.")

    # create course material
    material = CourseMaterialService.create_course_material(
        db=db, course_id=course_id, folder_id=folder_id, name=uploadFile.filename
    )

    # upload file to storage
    CourseMaterialService.update_course_material_status(db=db, material_id=material.id, status=CourseMaterialStatus.uploading)
    await CourseMaterialService.upload_course_material_to_storage(db=db, course_id=course_id, file_data=uploadFile)

    # process file
    CourseMaterialService.update_course_material_status(db=db, material_id=material.id, status=CourseMaterialStatus.processing)
    rows = await CourseMaterialUtils.get_file_embeddings(id=material.id, file_data=uploadFile)

    # store embeddings
    CourseMaterialService.store_embeddings_by_batch(db=db, rows=rows)
    CourseMaterialService.update_course_material_status(db=db, material_id=material.id, status=CourseMaterialStatus.ready)

    # return course material
    return CourseMaterialService.get_course_material(db=db, material_id=material.id)
