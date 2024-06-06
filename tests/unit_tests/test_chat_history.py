import setup

from tests.utils import assert_messages

from db.supabase import create_supabase_client
from utils.chat_message_history import SupabaseChatMessageHistory
from utils.datetime import get_current_timestamp

from routes.course.services import create_course, delete_course

from routes.course_members.services import (
    add_course_members,
    delete_course_members,
)
from routes.course_members.schemas import CourseMemberRequestItem

from routes.course_chats.schemas import CourseChatCreateRequest
from routes.course_chats.services import create_course_chat, delete_course_chat

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Supabase Client
client = create_supabase_client()


def test_sync_chat_history():
    """Test adding, reading, and clearing messages with SupabaseChatMessageHistory"""

    # Create course
    course = create_course(
        db=client, title="Test Course {}".format(get_current_timestamp())
    )
    course_id = course.id

    # Create course member
    member = add_course_members(
        db=client,
        course_id=course_id,
        members=[
            CourseMemberRequestItem(
                email="testingUser@test.com", role="teacher"
            )
        ],
    )[0]
    member_id = member.id

    # Create chat
    chat = create_course_chat(
        db=client,
        course_id=course_id,
        member_id=member_id,
        data=CourseChatCreateRequest(
            title="Test Chat for Course {} - {}".format(
                course_id, get_current_timestamp()
            )
        ),
    )
    chat_id = chat.id

    # Create Chat Message History
    chat_history = SupabaseChatMessageHistory(
        client=client, table_name="course_chat_messages", chat_id=chat_id
    )

    # Check if messages are empty
    messages = chat_history.messages
    assert messages == []

    # Add messages
    chat_history.add_messages(
        [
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
        ]
    )

    # Get messages from the chat history
    messages = chat_history.messages
    assert_messages(
        messages,
        [
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
        ],
    )

    # Add more messages
    chat_history.add_messages(
        [
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
        ]
    )

    # Check messages
    messages = chat_history.messages
    assert_messages(
        messages,
        [
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
        ],
    )

    # Clear messages
    chat_history.clear()
    assert chat_history.messages == []

    # Delete entities
    delete_course_chat(db=client, chat_id=chat_id)
    delete_course_members(db=client, course_id=course_id, emails=[member.email])
    delete_course(db=client, course_id=course_id)
