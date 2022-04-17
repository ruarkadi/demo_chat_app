from datetime import datetime
from importlib.resources import contents
from itertools import count
from chat.utilities.exceptions import *
import mongoengine
import urllib
import unittest
from chat.services import users_service, chats_service, messages_service
from chat.utilities import otp
from chat.models.users_model import User
from chat.models.chats_model import Chat
from chat.models.messages_model import Message
from .utils.mock_totp import get_totp_token
import sys
from PIL import Image
from io import BytesIO

username = "admin"
password = "0pt!M@Lpassw05d"
db_name = "test_db"

client = mongoengine.connect(host=f"mongodb+srv://{username}:{urllib.parse.quote(password)}@chat.uitqb.mongodb.net/{db_name}?retryWrites=true&w=majority")

def teardown(client, db_name):
    client.drop_database(db_name)

def create_chat(users):

    return chats_service.create_chat('group', users[0].id, users, name="group_chat")

def create_users():

    users = [
        {
            'email' : "test_mail1@gmail.com",
            'firstName' : "test",
            'lastName' : "user",
            'password' : "!Mrgit126",
            'nickName' : "test_user1",
        },
        {
            'email' : "test_mail2@gmail.com",
            'firstName' : "test",
            'lastName' : "user",
            'password' : "!Mrgit126",
            'nickName' : "test_user2",
        },
        {
            'email' : "test_mail3@gmail.com",
            'firstName' : "test",
            'lastName' : "user",
            'password' : "!Mrgit126",
            'nickName' : "test_user3",
        },
        {
            'email' : "test_mail4@gmail.com",
            'firstName' : "test",
            'lastName' : "user",
            'password' : "!Mrgit126",
            'nickName' : "test_user4",
        }
    ]

    created_users = []
    for user in users:
        created_users.append(User.add_user(user['email'], user['firstName'], user['lastName'], user['nickName'], user['password'], icon_path=None, state="active"))

    return created_users

class Test_messages(unittest.TestCase):

    chat_id = '60f074d10e2834a5dca02b14'

    def tearDown(self) -> None:
        teardown(client, db_name)
        return super().tearDown()

    def setUp(self) -> None:
        self.users = create_users()
        return super().setUp()

    # def test_create_message_chunk(self):

    #     message_chunk = Message_chunks.add_message_chunk(self.chat_id, message_chunk_index=0)

    #     self.assertTrue(message_chunk.id, msg="message chunk was not created")

    # def test_message_chunk_unique(self):

    #     Message_chunks.add_message_chunk(self.chat_id, message_chunk_index=0)

    #     self.assertRaises(mongoengine.errors.NotUniqueError, Message_chunks.add_message_chunk, self.chat_id, message_chunk_index=0)

    def test_send_text_message(self):

        users = self.users

        chat = create_chat(users)

        text = "text"

        messages_service.send_message(chat.id, users[0], text)

        chat.reload()

        # message_chunk = Message_chunks.get_message_chunk_by_index_and_chat_id(chat.id, chat.last_message_chunk_index)

        # last_message = message_chunk.messages[-1]
        last_message = Message.get_last_message_by_chat_id(chat.id)

        self.assertEqual(last_message.sender.id, users[0].id, msg="Sender ID does not match")
        self.assertEqual(last_message.text, text, msg="the text does not match")
        self.assertEqual(last_message.attachmentType, "text", msg="The message type does not match")

        self.assertEqual(len(chat.participants[0].unreadMessages), 0, msg="The sender has unread messages count")
        self.assertFalse(chat.participants[0].chatUnread, msg="The sender has chat unread True")
        for participant in chat.participants[1:]:
            self.assertEqual(len(participant.unreadMessages), 1, msg=f"The participant {participant.nickName} does not have unread messages count")
            self.assertTrue(participant.chatUnread, msg=f"The participant {participant.nickName} does has chat unread True")

        self.assertEqual(chat.lastMessage['messageSummary'], text, msg="The last message summary does not match")
        self.assertEqual(chat.lastMessage['messageId'], last_message.id, msg="The message ID does not match")

        message_recipient_ids = list(map(lambda recipient: recipient.id, last_message.recipients))

        for participant in chat.participants[1:]:
            self.assertIn(participant.id, message_recipient_ids, msg='The participant ID is not in the message recipients')

        self.assertNotIn(chat.participants[0].id, message_recipient_ids, msg='The message sender should not be in message recipients list')


    def test_get_last_message_by_chat_id(self):

        users = self.users

        chat = create_chat(users)

        text = "text"

        last_message = Message.get_last_message_by_chat_id(chat.id)
        self.assertIsNone(last_message, msg='The result should be None when no messages in chat')

        messages_service.send_message(chat.id, users[0], text)

        chat.reload()

        last_message = Message.get_last_message_by_chat_id(chat.id)

        self.assertEqual(last_message.sender.id, users[0].id, msg="Sender ID does not match")
        self.assertEqual(last_message.text, text, msg="the text does not match")
        self.assertEqual(last_message.attachmentType, "text", msg="The message type does not match")

        last_message = Message.get_last_message_by_chat_id(self.chat_id)
        self.assertIsNone(last_message, msg='The result should be None when chat not exist')

    # def test_send_massive_text_message(self):

    #     users = self.users

    #     chat = create_chat(users)

    #     text = "text"

    #     for i in range(10):
    #         messages_service.send_message(chat.id, users[0], text)

    #     chat.reload()

    def test_read_text_message(self):

        users = self.users

        chat = create_chat(users)

        text = "text"

        messages_service.send_message(chat.id, users[0], text)

        chats_service.mark_read_chat_messages_by_participant(chat.id, users[1].id)

        chat.reload()

        last_message = Message.get_last_message_by_chat_id(chat.id)

        participant = chat.get_participant_by_user_id(users[1].id)

        self.assertNotIn(last_message.id, participant.unreadMessages, msg='The message should not be in the participant unreadMessages list')
        self.assertFalse(participant.chatUnread, msg='The participant chatUnread should be False')

        recipient = last_message.get_recipient_by_user_id(users[1].id)
        self.assertTrue(recipient.readTimestamp, msg='There should be a readTimestamp on the message')
        self.assertFalse(last_message.readByAll, msg='The message should not be marked as read by all recipients')

        for other_recipient in [users[2], users[3]]:
            chats_service.mark_read_chat_messages_by_participant(chat.id, other_recipient.id)

        last_message.reload()

        self.assertTrue(last_message.readByAll, msg='The message should be marked as read by all recipients')

    def test_delete_message(self):

        users = self.users

        chat = create_chat(users)

        text = "text"

        messages_service.send_message(chat.id, users[0], text)

        first_message = Message.get_last_message_by_chat_id(chat.id)

        messages_service.send_message(chat.id, users[0], text)

        second_message = Message.get_last_message_by_chat_id(chat.id)

        chats_service.mark_read_chat_messages_by_participant(chat.id, users[1].id)

        chat.reload()

        second_message.reload()

        self.assertFalse(second_message.deleted, msg='The message should not be marked as deleted')

        messages_service.delete_message(second_message.id, users[0].id)

        second_message.reload()
        chat.reload()

        self.assertTrue(second_message.deleted, msg='The message should be marked as deleted')

        for participant in chat.participants:
            if participant.id == users[0].id:
                continue
            self.assertNotIn(second_message.id, participant.unreadMessages, msg=f"The deleted message should not be in {participant.nickName} unread messages")

            if participant.id == users[1].id:
                self.assertFalse(participant.chatUnread, msg=f"The chat unread flag for participant {participant.nickName} should be False")
            else:
                self.assertTrue(participant.chatUnread, msg=f"The chat unread flag for participant {participant.nickName} should be True due to second message")

        messages_service.delete_message(first_message.id, users[0].id)

        first_message.reload()
        chat.reload()

        self.assertTrue(first_message.deleted, msg='The message should be marked as deleted')

        for participant in chat.participants:
            if participant.id == users[0].id:
                continue
            self.assertNotIn(first_message.id, participant.unreadMessages, msg=f"The deleted message should not be in {participant.nickName} unread messages")
            self.assertFalse(participant.chatUnread, msg=f"The chat unread flag for participant {participant.nickName} should be False")

        messages_service.send_message(chat.id, users[0], text)

        third_message = Message.get_last_message_by_chat_id(chat.id)

        self.assertRaises(UserMessageDeletePermissionsError, messages_service.delete_message, third_message.id, users[1].id)

        for recipient in second_message.recipients:
            if recipient.id == users[1].id:
                self.assertTrue(recipient.readTimestamp, msg=f"The message readTimestamp for participant {recipient.nickName} should exist")
            else:
                self.assertFalse(recipient.readTimestamp, msg=f"The message readTimestamp for participant {recipient.nickName} should not exist")

    def test_get_messages(self):

        users = self.users

        chat = create_chat(users)

        text = "text"

        message_count = 24

        for i in range(message_count):
            messages_service.send_message(chat.id, users[0], text + f"{i}")

        chat.reload()

        messages = messages_service.get_messages(chat.id, users[1].id)

        self.assertEqual(len(messages), 20, msg='messages did not return the expected 20 messages')

        last_timestamp=datetime.utcnow()

        for message in messages:
            message_count -= 1
            self.assertGreater(last_timestamp, message.datetime)
            last_timestamp = message.datetime
            self.assertEqual(text + f"{str(message_count)}", message.text, msg=f"message text {message.text} does not match the expected text {text + str(message_count)}")


        chats_service.remove_group_chat_participants(chat, users[0].id, [chat.participants[1]])

        # Message sent while user 1 is removed from the chat
        messages_service.send_message(chat.id, users[0], text + " user should not see")

        messages_user1 = messages_service.get_messages(chat.id, users[1].id)
        messages_user2 = messages_service.get_messages(chat.id, users[2].id)

        self.assertNotEqual(messages_user1[0].id, messages_user2[0].id, msg=f"User {users[1].nickName} should not see the message while removed")

        chats_service.add_group_chat_participants(chat, users[0].id, [users[1]])

        messages_service.send_message(chat.id, users[0], text + " user should see")

        messages_user1 = messages_service.get_messages(chat.id, users[1].id)
        messages_user2 = messages_service.get_messages(chat.id, users[2].id)

        self.assertEqual(messages_user1[0].id, messages_user2[0].id, msg=f"User {users[1].nickName} should see the message sent to the group chat")

        self.assertRaises(UserNotInChat, messages_service.get_messages, chat.id, chat.id)
        self.assertRaises(ChatNotExist, messages_service.get_messages, users[1].id, chat.id)
