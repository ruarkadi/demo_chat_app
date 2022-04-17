# Mongoengine is an ODM
from cgitb import text

from .users_model import User
import mongoengine
import datetime
from mongoengine.queryset.visitor import Q
import filetype

from ..utilities.filetype_validation import is_image, is_video

from ..utilities import utils, db_utils

from mongoengine.base.fields import ObjectIdField, ObjectId


# This model is responsible for user CRUD operations

class Sender(mongoengine.EmbeddedDocument):

    meta = {'allow_inheritance': True}

    id = mongoengine.ObjectIdField(required= True)
    nickName = mongoengine.StringField(min_length=2, max_length=20, required=True)

class Recipient(Sender):
    readTimestamp = db_utils.TimeStampField()

# TODO: What about preview?
class Message(mongoengine.Document):

    meta = {
        'collection': 'messages',
        'ordering': ['-datetime'],
        'indexes': [
            {
                'fields': ['chat_id', '-datetime'],
                'name': 'message_desc_sorting_index'
            }
        ]
    }

    chat_id = mongoengine.ObjectIdField(required=True)
    sender = mongoengine.EmbeddedDocumentField(Sender, required=True)
    datetime = db_utils.TimeStampField(default=datetime.datetime.utcnow)
    text = mongoengine.StringField()
    attachmentPath = mongoengine.StringField()
    attachmentType = mongoengine.StringField(choices=["text", "image", "video"], required=True)
    recipients = mongoengine.EmbeddedDocumentListField(Recipient)
    readByAll = mongoengine.BooleanField(default=False)
    messageSummary = mongoengine.StringField()
    deleted = mongoengine.BooleanField(default=False)

    @staticmethod
    def add_message(chat_id, sender, recipients_list, text, attachment_type="text", attachment_path=None):

        if not isinstance(sender, User):
            raise TypeError("The sender was not a user")

        if not isinstance(text, str):
            raise TypeError("The text field is not a str")

        recipients = [Recipient(id=recipient['id'], nickName=recipient['nickName']) for recipient in recipients_list]

        text = text.strip()

        content = text if attachment_type == "text" else attachment_path

        if not Message.is_type_valid(attachment_type, content):
            err = "Attachment type text is empty" if attachment_type == "text" else f"Attachement is not a supported {attachment_type} type"
            raise Exception(err)

        # TODO: Add path validation once we figure out how we want to impelement this

        sender = Sender(id=sender.id, nickName=sender.nickName)

        message = Message(chat_id=chat_id, sender=sender, recipients=recipients, attachmentType=attachment_type, attachmentPath=attachment_path, text=text)

        message.create_summary()

        return message

    @staticmethod
    def is_type_valid(attachment_type, content):

        image_types = ['jpeg', 'png', 'bmp', 'gif', 'webp']
        video_types = ['mp4', 'avi', 'flv', 'mov', 'wmv']

        if attachment_type == "text" and not text:
            return False

        if attachment_type == "video" and not is_video(content, video_types):
            return False

        if attachment_type == "image" and not is_image(content, image_types):
            return False

        return True

    def create_summary(self):

        summary = ""
        content = ""

        if self.attachmentType == "video" or self.attachmentType == "image":
            summary += f"{{icon_{self.attachmentType}}}"
            content = self.attachmentType.capitalize()

        summary += self.text if self.text else content

        self.messageSummary = summary

    @staticmethod
    def get_last_message_by_chat_id(chat_id):
        return Message.objects(chat_id=chat_id).first()

    @staticmethod
    def get_messages(message_ids):
        return Message.objects(id__in=message_ids)

    @staticmethod
    def get_message_by_id(message_id):
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            message = None

        return message

    def get_recipient_by_user_id(self, user_id):
        user = self.recipients.filter(id=user_id)
        if not user:
            return None
        return user[0]

    def mark_message_as_read(self, recipient_id):
        recipient = self.get_recipient_by_user_id(recipient_id)
        recipient.readTimestamp = datetime.datetime.utcnow()
        if self.is_read_by_all():
            self.readByAll = True

    def is_read_by_all(self):
        return all([True if recipient.readTimestamp else False for recipient in self.recipients])

    def delete_message(self):
        self.deleted = True

    @staticmethod
    def get_messages_from_timestamp(chat_id, membership_sub_query=None ,timestamp=None, limit=20):

        query = {
            '$and': [
                {
                    'chat_id': { '$eq': ObjectId(chat_id) }
                },
                {
                    'deleted': { '$eq': False }
                },
                {
                    'datetime': { '$lte': timestamp if timestamp else datetime.datetime.utcnow().timestamp() }
                }
            ]
        }

        if membership_sub_query:
            query['$and'].append(membership_sub_query)

        print(query)
        print(limit)

        return Message.objects(__raw__=query).limit(limit)

# import datetime
# print(type(datetime.datetime.utcnow().timestamp()))

#         participant = self.get_participant_by_user_id(participant_id)

#         membership_conditions = []

#         for membership in participant.membership.reverse():

#             membership_condition = { 'datetime' : { '$gte' : membership['start'] } }

#             if 'end' in membership:
#                 membership_condition['datetime']['$lte'] = membership['end']

#         return { '$or': membership_conditions } if len(membership_conditions) > 1 else membership_conditions[0]

#   $and: [
#     {
#       chat_id: { $eq: "12345"}
#     },
#     {
#       deleted: { $eq : true }
#     },
#     {
#       ts: { $lte : 40 }
#     },
#     {
#         $or: [
#             { ts : { $gte : 1, $lte : 9 } },
#             { ts : { $gte : 11, $lte : 20 } },
#             { ts : { $gte : 45 } }
#         ]
#     }
#   ]