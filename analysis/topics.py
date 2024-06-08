from pydantic import BaseModel
from typing import List

import instructor
from openai import OpenAI

from routes.course_chat_topics.schemas import CourseChatTopic

instructor_client = instructor.from_openai(OpenAI())


class NewTopicsExtractorResponse(BaseModel):
    new_topics: List[str]


def extract_new_topics(
    existing_topics: List[CourseChatTopic], new_topics: List[str]
) -> List[str]:
    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting new topics by comparing two lists.Compare new topics with existing topics by meaning and remove duplicate topics that exist in the first list.",
        },
        {
            "role": "user",
            "content": "Existing topics: "
            + str([topic.name for topic in existing_topics])
            + "\nNew topics: "
            + str(new_topics),
        },
    ]

    result = instructor_client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=NewTopicsExtractorResponse,
        messages=messages,
    )

    return result.new_topics
