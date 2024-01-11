from fastapi import UploadFile
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import tempfile
import time
from db.vectorstore import embedding_model


async def process_file(file: UploadFile, loader_class, file_id: int):
    documents = []
    dateshort = time.strftime("%Y%m%d")

    with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp_file:
        await file.seek(0)
        content = await file.read()
        tmp_file.write(content)
        tmp_file.flush()

        loader = loader_class(tmp_file.name)
        docs = loader.load()

    os.remove(tmp_file.name)
    chunk_size = 500
    chunk_overlap = 0

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    texts = []
    documents: list[Document] = []
    metadatas = []
    for docIndex, doc in enumerate(text_splitter.split_documents(docs)):
        metadata = {
            "file_id": file_id,
            "chunk_index": docIndex,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "date": dateshort,
        }

        texts.append(doc.page_content)
        documents.append(Document(page_content=doc.page_content, metadata=metadata))
        metadatas.append(metadata)

    embeddings = embedding_model.embed_documents(texts)

    return documents, embeddings
