import setup

from routes.course_chat_topics.schemas import CourseChatTopic

from analysis.topics import extract_new_and_old_topics, extract_topics


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

    existing_topics = [
        CourseChatTopic(id=id, name=name, course_id=1, count=1, created_at="")
        for id, name in enumerate(existing_topic_names)
    ]
    existing_topic_ids = [topic.id for topic in existing_topics]
    print("Existing topic IDs:", existing_topic_ids)

    topics = extract_new_and_old_topics(
        existing_topics=existing_topics,
        new_topics=new_topics,
    )
    print("Topics:", topics)

    # Assertion to check none of the existing topic names are in the result
    for existing_topic in existing_topic_names:
        assert (
            existing_topic not in topics.new_topics
        ), f"Found existing topic '{existing_topic}' in result"

    # Check if existing topic IDs are in the result
    for topic_id in existing_topic_ids:
        assert (
            topic_id in topics.used_topic_ids
        ), f"Existing topic id={topic_id} missing in used topic ids={topics.used_topic_ids}"
