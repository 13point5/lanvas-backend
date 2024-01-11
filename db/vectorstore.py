from .supabase import create_supabase_client
from settings import OpenAIEnvVars

from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.supabase import SupabaseVectorStore
from langchain.docstore.document import Document

openAIEnvVars = OpenAIEnvVars()

supabase_client = create_supabase_client()

embedding_model = OpenAIEmbeddings(openai_api_key=openAIEnvVars.openai_api_key)


def get_similar_documents_from_files(query: str, match_count: int = 4, file_ids: list[int] = []) -> list[Document]:
    if len(file_ids) < 1:
        raise ValueError("file_ids must be a non-empty list")

    query_embedding = embedding_model.embed_query(query)

    res = supabase_client.rpc(
        "match_documents_by_file_ids",
        {"query_embedding": query_embedding, "match_count": match_count, "file_ids": file_ids},
    ).execute()

    documents = [
        Document(
            metadata={
                **search.get("metadata", {}),
                "id": search.get("id", ""),
                "similarity": search.get("similarity", 0.0),
            },
            page_content=search.get("content", ""),
        )
        for search in res.data
        if search.get("content")
    ]

    return documents
