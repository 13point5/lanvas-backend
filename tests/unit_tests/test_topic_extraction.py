import setup

from routes.course_chat_topics.schemas import CourseChatTopic

from analysis.topics import extract_new_topics, extract_topics


def test_topic_extractor():
    message = "what is learning design?"
    topics = extract_topics(message=message)

    print("Message:", message)
    print("Topics found:", topics)

    assert len(topics) != 0, f"Found 0 topics from message: {message}"


def test_unique_topic_extractor():
    existing_topic_names = ["learning design"]
    new_topics = existing_topic_names + [
        "design process",
        "instructional design",
    ]

    result_topic_names = extract_new_topics(
        existing_topics=[
            CourseChatTopic(id=id, name=name, course_id=1, created_at="")
            for id, name in enumerate(existing_topic_names)
        ],
        new_topics=new_topics,
    )

    # Assertion to check none of the existing topic names are in the result
    for existing_topic in existing_topic_names:
        assert (
            existing_topic not in result_topic_names
        ), f"Found existing topic '{existing_topic}' in result"
