import os
from fastapi import UploadFile

from parsers.pdf import process_pdf

file_processors = {
    ".pdf": process_pdf,
}


def get_file_extension(file_data: UploadFile) -> str:
    return os.path.splitext(file_data.filename)[-1]


def is_file_type_supported(file_data: UploadFile) -> bool:
    file_extension = get_file_extension(file_data)
    return file_extension in file_processors


async def get_file_embeddings(id: int, file_data: UploadFile):
    file_extension = get_file_extension(file_data)
    loader_class = file_processors[file_extension]
    documents, embeddings = await loader_class(file_data, file_id=id)
    rows = [
        {
            "content": doc.page_content,
            "embedding": embeddings[index],
            "metadata": doc.metadata,
        }
        for index, doc in enumerate(documents)
    ]

    return rows
