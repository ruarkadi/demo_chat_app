from enum import unique
from os import error, urandom
# Mongoengine is an ODM
import mongoengine
import datetime
from ..utilities import encryption, password_strength, otp, utils, db_utils
from ..utilities.exceptions import PasswordStrengthError
# This model is responsible for user CRUD operations

class User(mongoengine.Document):

    meta = {'collection': 'users'}

    email = mongoengine.EmailField(unique=True, required=True)
    firstName = mongoengine.StringField(min_length=2, max_length=20, required=True)
    lastName = mongoengine.StringField(min_length=2, max_length=20, required=True)
    nickName = mongoengine.StringField(unique=True, min_length=2, max_length=20, required=True)
    password = mongoengine.BinaryField(required=True)
    otp_key = mongoengine.StringField(min_length=32, max_length=32)
    icon = mongoengine.ImageField(size=(400, 400, True), thumbnail_size=(50,50, True))
    state = mongoengine.StringField(choices=["active", "disabled", "pending"], required = True)
    lastLogin = db_utils.TimeStampField(default=datetime.datetime.utcnow)
    lastActive = db_utils.TimeStampField(default=datetime.datetime.utcnow)
    verificationCode = mongoengine.StringField(min_length=6)
    chats = mongoengine.ListField()

    @staticmethod
    def add_user(email, firstName, lastName, nickName, password, icon_path=None, state="pending"):
        user = User(email=email, firstName=firstName, lastName=lastName, nickName=nickName, state=state)

        if icon_path:
            user.update_icon(icon_path)

        user.update_password(password)

        if state == "pending":
            user.update_verification_code()

        user.save()

        return user

    @staticmethod
    def get_user_by_email(email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        return user

    @staticmethod
    def get_user_by_id(id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            user = None

        return user

    @staticmethod
    def get_users_by_ids(user_ids):
        return User.objects(id__in=user_ids)

    def validate_password(self, password):
        return encryption.validate(password, self.password[32:], self.password[:32])

    def update_password(self, password):

        password_errors = password_strength.get_password_strength_errors(password)

        if password_errors:
            raise PasswordStrengthError(password_errors)

        self.set_encrypted_password(password)

    def updateLastLogin(self):
        self.lastLogin = datetime.datetime.utcnow()

    def set_encrypted_password(self, password):
        user_salt = encryption.generate_salt()
        user_encrypted_pass = encryption.encrypt(password, user_salt)
        self.password = user_salt + user_encrypted_pass

    def update_otp_key(self):
        self.otp_key = otp.get_secret_key()

    def update_verification_code(self):
        self.verificationCode = utils.generate_random_string()

    def update_icon(self, icon_path):

        if utils.is_file_exists(icon_path):
            with open(icon_path, 'rb') as file:
                self.icon.put(file)

    def updateLastActive(self):
        self.lastActive = datetime.datetime.utcnow()

    def add_chat_to_user(self, chat_id):
        self.chats.append({ "id": chat_id, "status": "active" })

    def remove_chat_from_user(self, chat_id, is_deleted=False):
        index = self.chats.index(next(filter(lambda chat: chat['id'] == chat_id, self.chats)))
        if not is_deleted:
            self.chats[index]['status'] = "disabled"
        else:
            self.chats.pop(index)

