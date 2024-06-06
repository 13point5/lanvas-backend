import json
from typing import List, Optional, Sequence

from supabase import Client


from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)


class SupabaseChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in a Supabase table"""

    def __init__(self, chat_id: int, table_name: str, client: Client) -> None:
        self.client = client
        self.table_name = table_name
        self.chat_id = chat_id

    @property
    def messages(self) -> List[BaseMessage]:
        res = (
            self.client.table(self.table_name)
            .select("*")
            .eq("chat_id", self.chat_id)
            .execute()
            .data
        )

        messages = [
            {
                "type": message["role"],
                "data": {
                    "content": message["content"],
                    "id": message["id"],
                    "metadata": message["metadata"],
                },
            }
            for message in res
        ]

        return messages_from_dict(messages)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        rows = [
            {
                "chat_id": self.chat_id,
                "role": message.type,
                "content": message.content,
                "metadata": {},
            }
            for message in messages
        ]

        self.client.table(self.table_name).insert(rows).execute()

    def clear(self):
        self.client.table(self.table_name).delete().eq(
            "chat_id", self.chat_id
        ).execute().data
