from typing import List

from langchain_core.messages import BaseMessage


def assert_messages(
    actual_messages: List[BaseMessage], expected_messages: List[BaseMessage]
):
    assert len(actual_messages) == len(expected_messages), (
        f"Number of messages does not match: "
        f"{len(actual_messages)} != {len(expected_messages)}"
    )

    for actual, expected in zip(actual_messages, expected_messages):
        assert actual.type == expected.type, (
            f"Message Types do not match: " f"{actual.type} != {expected.type}"
        )

        assert actual.content == expected.content, (
            f"Message Contents do not match: "
            f"{actual.content} != {expected.content}"
        )
