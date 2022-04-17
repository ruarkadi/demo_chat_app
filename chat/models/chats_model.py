from email.policy import default
from os import error, name, urandom
# Mongoengine is an ODM
import mongoengine
import datetime

from mongoengine.queryset.visitor import Q
from ..utilities import utils, db_utils
from ..utilities.exceptions import *

from mongoengine.base.fields import ObjectIdField

class Membership(mongoengine.EmbeddedDocument):
    start = db_utils.TimeStampField(default=datetime.datetime.utcnow)
    end = db_utils.TimeStampField()

class ChatParticipant(mongoengine.EmbeddedDocument):
    id = mongoengine.ObjectIdField(required=True)
    nickName = mongoengine.StringField(min_length=2, max_length=20, required=True)
    status = mongoengine.StringField(choices=["active", "disabled"], required=True, default="active")
    isAdmin = mongoengine.BooleanField(default=False)
    unreadMessages = mongoengine.ListField()
    chatUnread = mongoengine.BooleanField(default=False)
    membership = mongoengine.EmbeddedDocumentListField(Membership, required=True)

class ChatLastMessage(mongoengine.EmbeddedDocument):
    messageId = mongoengine.ObjectIdField()
    messageSummary = mongoengine.StringField()

class Chat(mongoengine.Document):

    meta = {'collection': 'chats'}

    name = mongoengine.StringField(min_length=2, max_length=20)
    createdAt = db_utils.TimeStampField(default=datetime.datetime.utcnow)
    participants = mongoengine.EmbeddedDocumentListField(ChatParticipant, required=True)
    icon = mongoengine.ImageField(size=(400, 400, True), thumbnail_size=(50,50, True))
    lastMessage = mongoengine.EmbeddedDocumentField(ChatLastMessage)
    chattype = mongoengine.StringField(choices = ["private", "group"], required = True)

    @staticmethod
    def add_chat(chattype, participants, name = None, icon_path = None):
        if chattype != "private" and not name:
            raise MissingArg("A name is required")

        if chattype == "private" and len(participants) != 2:
            raise ChatValidationError("Private chat can only contain two participants")

        if chattype == "private" and Chat.get_private_chat_by_participants(participants[0]['nickName'], participants[1]['nickName']):
            raise ChatAlreadyExists("Private chat already exists")

        if chattype == "private" and icon_path:
            raise ChatValidationError("Private chats cannot have a custom icon")

        chat = Chat(chattype = chattype, name = name)

        if icon_path:
            chat.update_icon(icon_path)

        chat.add_participants(participants, is_create=True)

        chat.save()

        return chat

    def update_icon(self, icon_path):

        if utils.is_file_exists(icon_path):
            with open(icon_path, 'rb') as file:
                self.icon.put(file, content_type = 'image/jpeg')

    @staticmethod
    def get_private_chat_by_participants(user_a, user_b):
        return Chat.objects(__raw__={ '$and': [{"participants.nickName": {'$eq': user_a }}, {"participants.nickName": {'$eq': user_b }}]}).limit(1)

    @staticmethod
    def get_chats(chat_ids):
        return Chat.objects(id__in=chat_ids)

    @staticmethod
    def get_chat_by_id(chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            chat = None

        return chat

    def add_participants(self, participants, is_create=False):
        id_list = {str(id['id']):id['status'] for id in self.participants}

        for index, participant in enumerate(participants):
            p = ChatParticipant(id = participant['id'], nickName = participant['nickName'], status = "active")

            if is_create and self.chattype != "private" and index == 0:
                p.isAdmin=True

            if participant['id'] in id_list:
                if id_list[ participant['id'] ] == 'disabled':
                    existing_participant = self.participants.filter(id=participant['id'])
                    existing_participant[0].status = "active"
                    self.set_membership_add_date(existing_participant[0])
            else:
                self.participants.append(p)
                self.set_membership_add_date(p)

    def remove_participants(self, participants):
        removed_participant_ids = []
        for participant in participants:
            participant_object = self.participants.filter(id=participant['id'])
            if participant_object:
                self.change_participant_role(participant_object[0], False)
                participant_object[0].status = "disabled"
                self.set_membership_remove_date(participant_object[0])
                removed_participant_ids.append(participant_object[0].id)

        return removed_participant_ids

    def get_group_admins(self):
        return self.participants.filter(isAdmin=True, status="active")

    def get_active_participants(self):
        return self.participants.filter(status="active")

    def get_active_participant_by_user_id(self, user_id):
        user = self.participants.filter(id=user_id, status="active")
        if not user:
            return None
        return user[0]

    def get_participant_by_user_id(self, user_id):
        user = self.participants.filter(id=user_id)
        if not user:
            return None
        return user[0]

    def get_participants_by_user_ids(self, user_id_list):

        return [participant for participant in self.participants if str(participant.id) in user_id_list]

    def get_active_participants_by_user_ids(self, user_id_list):

        return [participant for participant in self.participants if str(participant.id) in user_id_list and participant.status == "active"]

    def change_participant_role(self, participant, isAdmin):
        participant.isAdmin = isAdmin

    def promote_first_active_participant(self):
        active_participants = self.get_active_participants()
        if not len(self.get_group_admins()) and len(active_participants):
            self.change_participant_role(active_participants[0], True)

    def mark_participants_unread(self, sender_id, message_id):
        participants = self.get_active_participants()

        for participant in participants:
            if sender_id == participant.id:
                continue

            participant.unreadMessages.append(message_id)
            participant.chatUnread = True

    def update_last_message(self, message_id, message_summary):
        self.lastMessage = ChatLastMessage(messageId=message_id, messageSummary=message_summary)

    def set_membership_remove_date(self, participant):
        participant.membership[-1].end = datetime.datetime.utcnow()

    def set_membership_add_date(self, participant):
        membership = Membership()
        participant.membership.append(membership)

    def mark_read_chat_by_participant(self, participant_id):
        participant = self.get_active_participant_by_user_id(participant_id)
        participant.unreadMessages = []
        participant.chatUnread = False

    def mark_read_chat_message_by_participant(self, participant_id, message_id):
        participant = self.get_active_participant_by_user_id(participant_id)
        if message_id in participant.unreadMessages:
            participant.unreadMessages.remove(message_id)
        participant.chatUnread = bool(len(participant.unreadMessages))

    def prepare_membership_mongodb_query(self, participant_id):

        participant = self.get_participant_by_user_id(participant_id)

        membership_conditions = []

        for membership in reversed(participant.membership):

            membership_condition = { 'datetime' : { '$gte' : membership['start'].timestamp() } }

            if 'end' in membership:
                membership_condition['datetime']['$lte'] = membership['end'].timestamp()

            membership_conditions.append(membership_condition)

        return { '$or': membership_conditions } if len(membership_conditions) > 1 else membership_conditions[0]

    def reset_participant_membership(self, participant):

        participant.membership = []





