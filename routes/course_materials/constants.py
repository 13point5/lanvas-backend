from enum import Enum

STORAGE_BUCKET = "course-materials"


class CourseMaterialStatus(str, Enum):
    uploading = "uploading"
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
