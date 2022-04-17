from asyncore import read
from datetime import datetime
from ntpath import join

from ..models.chats_model import Chat
from ..models.users_model import User
from ..models.messages_model import Message
# from ..models.messages_model import Message_chunks
# from ..models.messages_model import ChatMessages
from ..utilities.exceptions import *


def __users_to_participants(users):
    return list(map(lambda user : {"id" : str(user.id), "nickName" : user.nickName}, users))

def create_chat(chattype, req_user_id, user_ids, name = None, icon_path = None):

    users = []

    # Convert user ids to a list of user objects and quit entirely if a single ID does not exist. Because we're atomic.
    for user_id in user_ids:

        user = User.get_user_by_id(user_id)

        if not user:
            raise UserNotExist(f"A user with the following id {user_id} does not exist")

        users.append(user)

    req_user = User.get_user_by_id(req_user_id)

    if not req_user:
        raise UserNotExist('The requesting user does not exist')

    # Make sure that the requesting user is first in line (will be the first admin of the group, if it is public)
    try:
        req_user_index = users.index(req_user)
        if req_user_index > 0:
            users.pop(req_user_index)
            users.insert(0, req_user)

    except:
        raise UserNotExist('The requesting user is not in the users id list provided')

    participants = __users_to_participants(users)

    chat = Chat.add_chat(chattype, participants, name, icon_path)

    for user in users:
        user.add_chat_to_user(chat.id)
        user.save()

    # Message_chunks.add_message_chunk(chat.id, chat.last_message_chunk_index)

    return chat

# def delete_chat(chat, req_user_id):
#     if not __does_user_have_chat_permissions(chat, req_user_id):
#         raise UserChatPermissionsError('The user does not have permissions on the chat')
#     # TODO: delete chat messages as well

#     for participant in chat.participants:
#         user = User.get_user_by_id(participant['id'])
#         user.remove_chat_from_user(chat.id, is_deleted=True)
#         user.save()

#     chat.delete()
#     return True

def update_chat(chat_id, req_user_id, name=None, icon_path=None):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    if not __does_user_have_chat_permissions(chat, req_user_id):
        raise UserChatPermissionsError('The user does not have permissions on the chat')
    if name:
        chat.name = name
    if icon_path:
        chat.update_icon(icon_path)

    chat.save()

    return chat

def get_chat(chat_id, req_user_id):
    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    if not __was_user_in_chat(chat, req_user_id):
        raise UserChatPermissionsError('The user is not a participant in chat')

    return chat

def get_chats_by_user(user):
    chat_id_list = [chat['id'] for chat in user.chats]
    return Chat.get_chats(chat_id_list)

def add_group_chat_participants(chat_id, req_user_id, req_user_ids):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    users = User.get_users_by_ids(req_user_ids)

    if not users or len(users) != len(req_user_ids):

        # Make a list from returned user objects to help in detecting values which were not found in the passed user_ids
        found_user_ids = [str(user['id']) for user in users]

        not_found_user_ids = list(set(req_user_ids) - set(found_user_ids))

        raise ParticipantsNotExit(f"The following participants were not found: {', '.join(not_found_user_ids)}")

    participants = __users_to_participants(users)

    if not __does_user_have_chat_permissions(chat, req_user_id):
        raise UserChatPermissionsError('The user does not have permissions on the chat')

    chat.add_participants(participants)

    chat.save()

    for user in users:
        user.add_chat_to_user(chat.id)
        user.save()

    return chat.get_active_participants()

def remove_group_chat_participants(chat_id, req_user_id, participant_ids):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    if not __does_user_have_chat_permissions(chat, req_user_id):
        raise UserChatPermissionsError('The user does not have permissions on the chat')

    participants = chat.get_participants_by_user_ids(participant_ids)

    if len(participant_ids) != len(participants):

        # Make a list from returned user objects to help in detecting values which were not found in the passed user_ids
        found_participant_ids = [str(participant['id']) for participant in participants]

        not_found_participant_ids = list(set(participant_ids) - set(found_participant_ids))

        raise ParticipantsNotExit(f"The following participants were not found: {', '.join(not_found_participant_ids)}")

    __remove_participants(chat, participants)

    return chat.get_active_participants()

def leave_group_chats(req_user, chats):

    for chat in chats:

        participant = chat.get_participant_by_user_id(req_user.id)

        __remove_participants(chat, [participant])

def leave_group_chat(chat_id, req_user_id):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    participant = chat.get_participant_by_user_id(req_user_id)

    if not participant:
        raise ParticipantNotExit('The participant does not exist in chat')

    if not __is_user_active_in_chat(req_user_id) or __is_chat_private(chat):
        raise UserChatPermissionsError('User cannot be removed from chat')

    __remove_participants(chat, [participant])

    return True

def change_users_role(chat_id, req_user_id, participant_ids, admin_status=False):

    chat = Chat.get_chat_by_id(chat_id)

    if not chat:
        raise ChatNotExistError('The chat does not exist')

    if not __does_user_have_chat_permissions(chat, req_user_id):
        raise UserChatPermissionsError('The user does not have permissions on the chat')

    if str(req_user_id) in participant_ids:
        raise UserChatPermissionsError('The user can\'t change his own role')

    participants = chat.get_active_participants_by_user_ids(participant_ids)

    if len(participant_ids) != len(participants):

        # Make a list from returned user objects to help in detecting values which were not found in the passed user_ids
        found_participant_ids = [str(participant['id']) for participant in participants]

        not_found_participant_ids = list(set(participant_ids) - set(found_participant_ids))

        raise ParticipantsNotExit(f"The following participants were not found: {', '.join(not_found_participant_ids)}")

    for participant in participants:
        chat.change_participant_role(participant, admin_status)

    if not admin_status:
        chat.promote_first_active_participant()

    chat.save()

    return chat.get_active_participants()

def __is_user_admin(chat, user_id):
    participant=chat.get_active_participant_by_user_id(user_id)

    if not participant:
        return False

    return participant.isAdmin

def __is_chat_private(chat):

    return chat['chattype'] == 'private'

def __does_user_have_chat_permissions(chat, user_id):

    return __is_user_admin(chat, user_id) and not __is_chat_private(chat)

def mark_read_chat_messages_by_participant(chat_id, participant_id):

    chat = Chat.get_chat_by_id(chat_id)

    participant = chat.get_active_participant_by_user_id(participant_id)

    unread_messages = Message.get_messages(participant.unreadMessages)

    for message in unread_messages:
        message.mark_message_as_read(participant_id)
        message.save()

    chat.mark_read_chat_by_participant(participant_id)
    chat.save()

def __is_user_active_in_chat(chat, user_id):
    participant = chat.get_active_participant_by_user_id(user_id)

    return bool(participant)

def __was_user_in_chat(chat, user_id):
    return bool(chat.get_participant_by_user_id(user_id))

def __remove_participants(chat, participants):

    removed_participant_ids = chat.remove_participants(participants)

    chat.promote_first_active_participant()

    chat.save()

    for participant_id in removed_participant_ids:
        user = User.get_user_by_id(participant_id)
        user.remove_chat_from_user(chat.id)
        user.save()

def reset_participant_membership_in_chats(chats, user_id):

    for chat in chats:

        participant = chat.get_participant_by_user_id(user_id)

        chat.reset_participant_membership(participant)

        chat.save()