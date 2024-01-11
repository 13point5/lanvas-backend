from .main import process_file
from langchain.document_loaders import PyMuPDFLoader
from fastapi import UploadFile


def process_pdf(file: UploadFile, file_id: int):
    return process_file(file=file, loader_class=PyMuPDFLoader, file_id=file_id)
