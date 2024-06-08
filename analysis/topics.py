from pydantic import BaseModel
from typing import List

import instructor
from openai import OpenAI

from routes.course_chat_topics.schemas import CourseChatTopic

instructor_client = instructor.from_openai(OpenAI())


class TopicsExtractorResponse(BaseModel):
    topics: List[str]


def extract_topics(message: str) -> List[str]:
    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting topics discussed in a message by a student chatting with an AI tutor for a course. Extract unique topics and keep them concise.",
        },
        {"role": "user", "content": "Message: {}".format(message)},
    ]

    result = instructor_client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=TopicsExtractorResponse,
        messages=messages,
    )

    return result.topics


class NewTopicsExtractorResponse(BaseModel):
    new_topics: List[str]
    used_topic_ids: List[int]


def extract_new_and_old_topics(
    existing_topics: List[CourseChatTopic], new_topics: List[str]
) -> NewTopicsExtractorResponse:
    messages = [
        {
            "role": "system",
            "content": "You are an expert at extracting new topics by comparing two lists.Compare new topics with existing topics by meaning and remove duplicate topics in the new topics list that are already there in the existing topics list. You should also return the IDs of the topics that are used in both lists.",
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

    return result
