import warnings
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from .supabase import create_supabase_client
from settings import OpenAIEnvVars

from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain_community.vectorstores.supabase import SupabaseVectorStore

openAIEnvVars = OpenAIEnvVars()

supabase_client = create_supabase_client()

embedding_model = OpenAIEmbeddings(openai_api_key=openAIEnvVars.openai_api_key)


class CustomSupabaseVectorStore(SupabaseVectorStore):
    """
    A Custom SupabaseVectorStore which supports custom filters with retriever
    """

    def match_args(
        self,
        query: List[float],
        filter: Optional[Dict[str, Any]],
        custom_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ret: Dict[str, Any] = dict(query_embedding=query)

        if filter:
            ret["filter"] = filter

        if custom_filter:
            ret.update(custom_filter)

        return ret

    def similarity_search_by_vector_with_relevance_scores(
        self,
        query: List[float],
        k: int,
        filter: Optional[Dict[str, Any]] = None,
        postgrest_filter: Optional[str] = None,
        score_threshold: Optional[float] = None,
        custom_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        match_documents_params = self.match_args(query, filter, custom_filter)
        query_builder = self._client.rpc(
            self.query_name, match_documents_params
        )

        if postgrest_filter:
            query_builder.params = query_builder.params.set(
                "and", f"({postgrest_filter})"
            )

        query_builder.params = query_builder.params.set("limit", k)

        res = query_builder.execute()

        match_result = [
            (
                Document(
                    metadata=search.get("metadata", {}),  # type: ignore
                    page_content=search.get("content", ""),
                ),
                search.get("similarity", 0.0),
            )
            for search in res.data
            if search.get("content")
        ]

        if score_threshold is not None:
            match_result = [
                (doc, similarity)
                for doc, similarity in match_result
                if similarity >= score_threshold
            ]
            if len(match_result) == 0:
                warnings.warn(
                    "No relevant docs were retrieved using the relevance score"
                    f" threshold {score_threshold}"
                )

        return match_result


course_vectorstore = CustomSupabaseVectorStore(
    client=supabase_client,
    embedding=embedding_model,
    table_name="documents",
    query_name="match_documents_by_course_id",
)

# Example Usage of custom filter
# retriever = vectorstore.as_retriever(
#     search_kwargs={"custom_filter": {"course_id_arg": 20}}
# )
