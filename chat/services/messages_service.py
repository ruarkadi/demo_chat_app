from ..models.chats_model import Chat
from ..models.users_model import User
from ..models.messages_model import Message
from ..utilities.exceptions import *


def send_message(chat_id, user_id, text, attachment_type="text", attachment_path=None):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    user = User.get_user_by_id(user_id)

    if not user:
        raise UserNotExist("User does not exist")

    if not chat.get_active_participant_by_user_id(user.id):
        raise ParticipantNotExit("The sender needs to be a participant in the chat")

    message_recipients = [{'id': participant.id, 'nickName': participant.nickName} for participant in chat.participants if participant.id != user.id]

    message = Message.add_message(chat.id, user, message_recipients, text, attachment_type, attachment_path)

    message.save()

    chat.mark_participants_unread(user.id, message.id)

    chat.update_last_message(message.id, message.messageSummary)

    chat.save()

    return message

def delete_message(message_id, user_id):

    message = Message.get_message_by_id(message_id)

    if not message:
        raise MessageNotExit('Message not found')

    chat = Chat.get_chat_by_id(message.chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    if not chat.get_active_participant_by_user_id(user_id):
        raise ParticipantNotExit("The user needs to be a participant in the chat")

    if message.sender.id != user_id:
        raise UserMessageDeletePermissionsError("User can only delete own messages")

    for participant in chat.participants:

        if participant.id == user_id:
            continue

        # We want to mark the messages as read to remove them from the unread count
        chat.mark_read_chat_message_by_participant(participant.id, message_id)

    chat.save()

    message.delete_message()

    message.save()

def get_messages(chat_id, user_id, timestamp=None):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    user = User.get_user_by_id(user_id)

    if not user:
        raise UserNotExist("User does not exist")

    if not chat.get_participant_by_user_id(user_id):
        raise UserNotExistInChatError('The user was never a chat participant')

    membership_sub_query = chat.prepare_membership_mongodb_query(user_id)

    print(membership_sub_query)

    return Message.get_messages_from_timestamp(chat_id, membership_sub_query, timestamp)

# get message (see read by list in whatsapp)
def forward_message():
    pass


#     return money
