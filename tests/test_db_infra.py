from datetime import datetime
from importlib.resources import contents
from chat.utilities.exceptions import PasswordMismatch, PasswordStrengthError, UserChatPermissionsError
import mongoengine
import urllib
import unittest
from chat.services import users_service, chats_service
from chat.utilities import otp
from chat.models.users_model import User
from chat.models.chats_model import Chat
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

def create_participants_to_compare(participants, users, is_group=False):

    participants_list = []
    compare_participants_list = []

    for index, participant in enumerate(participants):

        participants_list.append(dict(participants[index].to_mongo()))

        compare_participants_list.append(
            {**participants_list[index], **{
                'id': users[index].id,
                'isAdmin': True if is_group and index == 0 else False
            }}
        )

    return participants_list, compare_participants_list

def get_simulated_pil_compression_content(file_path):


    with open(file_path, 'rb') as file:

        try:
            img = Image.open(file)
            img_format = img.format
        except Exception as e:
            raise Exception("Invalid image: %s" % e)

        io = BytesIO()
        img.save(io, img_format, progressive=False)
        io.seek(0)

    return io.read()

class Test_signup(unittest.TestCase):

    email = "test_mail@gmail.com"
    firstName = "test"
    lastName = "user"
    password = "!Mrgit126"
    confirm_password = "!Mrgit126"
    nickName = "test_user"
    icon_path = "tests/resources/twitter_profile_image_size.jpeg"

    def tearDown(self) -> None:
        teardown(client, db_name)
        return super().tearDown()

    def test_successful_signup(self):

        user = users_service.signup(self.email, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password, self.icon_path)

        self.assertTrue(user.id, msg="user was not created")

    def test_password_mismatch(self):

        confirm_password = "1"

        self.assertRaises(PasswordMismatch, users_service.signup, self.email, self.firstName, self.lastName, self.nickName, self.password, confirm_password)

    def test_password_strength(self):

        password = "mrgit1"
        confirm_password = "mrgit1"

        self.assertRaises(PasswordStrengthError, users_service.signup, self.email, self.firstName, self.lastName, self.nickName, password, confirm_password)

    def test_icon_path(self):

        icon_path="/icon.png"

        self.assertRaises(FileNotFoundError, users_service.signup, self.email, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password, icon_path)

    def test_email_verification(self):

        users_service.signup(self.email, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password, self.icon_path)

        self.assertRaises(mongoengine.errors.NotUniqueError, users_service.signup, self.email, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password)

        self.assertRaises(mongoengine.errors.ValidationError, users_service.signup, "ruarkadi", self.firstName, self.lastName, self.nickName, self.password, self.confirm_password)

        self.assertRaises(mongoengine.errors.ValidationError, users_service.signup, None, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password)

    def test_otp_config(self):

        user = users_service.signup(self.email, self.firstName, self.lastName, self.nickName, self.password, self.confirm_password)

        users_service.configure_otp(user)

        secret = user.otp_key

        code = get_totp_token(secret)

        self.assertTrue(otp.validate_otp(code, secret))
        self.assertFalse(otp.validate_otp("028476", secret))

class Test_chat(unittest.TestCase):

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
        }
    ]

    extra_users = [
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

    def tearDown(self) -> None:
        teardown(client, db_name)
        return super().tearDown()

    def create_users(self, users):

        created_users = []
        for user in users:
            created_users.append(User.add_user(user['email'], user['firstName'], user['lastName'], user['nickName'], user['password'], icon_path=None, state="active"))

        return created_users

    def test_private_chat_create(self):

        users = self.create_users(self.users)

        chat = chats_service.create_chat('private', users[0].id, users)

        self.assertTrue(chat.id, msg = 'chat not created')
        self.assertEqual(chat.chattype, 'private', msg="chattype mismatch")

        compare_lists = create_participants_to_compare(chat.participants, users)

        self.assertEqual(compare_lists[0], compare_lists[1], msg='users were not properly added as chat participants')

        for user in users:
            user.reload()
            self.assertIn({'id': chat.id, 'status': 'active'}, user['chats'], msg = f'the chat was not added to user {user["id"]} - {user["nickName"]}')

    def test_group_chat_create(self):

        users = self.create_users(self.users)

        chat = chats_service.create_chat('group', users[0].id, users, name="Test Group", icon_path="tests/resources/twitter_profile_image_size.jpeg")

        self.assertTrue(chat.id, msg = 'chat not created')
        self.assertEqual(chat.chattype, 'group', msg="chattype mismatch")

        for user in users:
            user.reload()
            self.assertIn({'id': chat.id, 'status': 'active'}, user['chats'], msg = f'the chat was not added to user {user["id"]} - {user["nickName"]}')

        self.assertTrue(chat.participants[0].isAdmin, msg='The creator of the chat is not an admin')
        self.assertFalse(chat.participants[1].isAdmin, msg='The member of the chat was added as an admin')


    def test_group_chat_massive_create(self):

        users = self.create_users(self.users)
        num_of_groups = 3

        for i in range(num_of_groups):
            chat = chats_service.create_chat('group', users[0].id, users, name=f"Test Group {i}", icon_path="tests/resources/twitter_profile_image_size.jpeg")

            self.assertTrue(chat.id, msg = 'chat not created')
            self.assertEqual(chat.chattype, 'group', msg="chattype mismatch")

            for user in users:
                user.reload()
                self.assertIn({'id': chat.id, 'status': 'active'}, user['chats'], msg = f'the chat was not added to user {user["id"]} - {user["nickName"]}')

            self.assertTrue(chat.participants[0].isAdmin, msg='The creator of the chat is not an admin')
            self.assertFalse(chat.participants[1].isAdmin, msg='The member of the chat was added as an admin')

        self.assertEqual(len(Chat.objects()), num_of_groups, msg='Amount of chats created does not equal the requested amount')


    def test_permissions_private_chat(self):

        users = self.create_users(self.users)
        extra_users = self.create_users(self.extra_users)

        chat = chats_service.create_chat('private', users[0].id, users)

        # self.assertRaises(UserChatPermissionsError, chats_service.delete_chat, chat, users[0].id)
        self.assertRaises(UserChatPermissionsError, chats_service.update_chat, chat, users[0].id, name="testing")

        self.assertRaises(UserChatPermissionsError, chats_service.add_group_chat_participants, chat, users[0].id, extra_users)

        chat.reload()

        self.assertEqual(len(chat['participants']), 2, msg='The amount of participants is not 2 as expected')

        for user in extra_users:
            user.reload()
            self.assertNotIn({'id': chat.id, 'status': 'active'}, user['chats'], msg = f'the chat was added to user {user["id"]} - {user["nickName"]}')

        self.assertRaises(UserChatPermissionsError, chats_service.remove_group_chat_participants, chat, users[0].id, [users[1]])

        self.assertIn({'id': chat.id, 'status': 'active'}, users[1]['chats'], msg = f'the chat was removed from user {users[1]["id"]} - {users[1]["nickName"]}')

        self.assertEqual(len(chat['participants']), 2, msg='The amount of participants is not 2 as expected')

        self.assertRaises(UserChatPermissionsError, chats_service.change_users_role, chat, users[0].id, [users[1].id], admin_status=True)

        self.assertRaises(UserChatPermissionsError, chats_service.change_users_role, chat, users[0].id, [users[1].id], admin_status=False)

    def test_group_chat_name(self):

        users = self.create_users(self.users)

        chat_names = [
            'צ׳אט',
            '!@#$',
            '&&&group_chats////',
            'צ׳אטchat',
            '______'
        ]

        for chat_name in chat_names:
            chat = chats_service.create_chat('group', users[0].id, users, name=chat_name)
            chat.reload()
            self.assertEqual(chat.name, chat_name, msg='The chat names are not equal')

    # def test_delete_group_chat(self):

    #     users = self.create_users(self.users)

    #     chat = chats_service.create_chat('group', users[0].id, users, name="group_chat")

    #     self.assertRaises(UserChatPermissionsError, chats_service.delete_chat, chat, users[1].id)

    #     is_deleted = chats_service.delete_chat(chat, users[0].id)
    #     self.assertTrue(is_deleted, msg='The chat was not deleted')

    #     is_chat_exist = chats_service.get_chat(chat.id)
    #     self.assertIsNone(is_chat_exist, msg='The chat still exists')

    #     for user in users:
    #         user.reload()
    #         self.assertFalse(any(user_chat.get('id') == chat.id for user_chat in user.chats), msg = f'the chat was not removed from user {user["id"]} - {user["nickName"]}')

    def test_update_group_chat(self):

        users = self.create_users(self.users)

        chat = chats_service.create_chat('group', users[0].id, users, name="group_chat")

        self.assertRaises(UserChatPermissionsError, chats_service.update_chat, chat, users[1].id, name="group_chat1")


        chats_service.update_chat(chat, users[0].id, name="group_chat1", icon_path="tests/resources/twitter_profile_image_size.jpeg")

        chat.reload()
        self.assertEqual(chat.name, "group_chat1", msg='The chat name was not updated')

        image_content_from_db = chat.icon.read()
        image_content_from_path = get_simulated_pil_compression_content("tests/resources/twitter_profile_image_size.jpeg")

        self.assertEqual(image_content_from_path, image_content_from_db, msg='There is a difference between icon from path and icon in db')

    def test_permissions_group_chat(self):

        users = self.create_users(self.users)
        extra_users = self.create_users(self.extra_users)

        chat = chats_service.create_chat('group', users[0].id, users, name="group_chat")

        chats_service.add_group_chat_participants(chat, users[0].id, extra_users)
        chat.reload()

        compare_lists = create_participants_to_compare(chat.participants, users + extra_users, is_group=True)

        self.assertEqual(compare_lists[0], compare_lists[1], msg='users were not properly added as chat participants')

        for user in extra_users:
            user.reload()
            self.assertIn({'id': chat.id, 'status': 'active'}, user['chats'], msg = f'the chat was not added to user {user["id"]} - {user["nickName"]}')

        chats_service.change_users_role(chat, users[0].id, [chat.participants[2]['id'], chat.participants[3]['id']], admin_status=True)

        self.assertTrue(chat.participants[2].isAdmin, msg="The user was not promoted to group admin")

        chats_service.change_users_role(chat, users[0].id, [chat.participants[2]['id']], admin_status=False)

        self.assertFalse(chat.participants[2].isAdmin, msg="The user was not removed as group admin")

        self.assertRaises(UserChatPermissionsError, chats_service.change_users_role, chat, users[1].id, [chat.participants[2]['id']], admin_status=True)

        self.assertRaises(UserChatPermissionsError, chats_service.add_group_chat_participants, chat, users[1].id, extra_users)

        chats_service.remove_group_chat_participants(chat, users[0].id, [chat.participants[3]])

        expected_removal_result = {'id': extra_users[1].id, 'isAdmin': False, 'status': 'disabled'}

        self.assertEqual(dict(chat.participants[3].to_mongo()), {**dict(chat.participants[3].to_mongo()), **expected_removal_result}, msg='The admin user was not properly removed from the group')

        extra_users[1].reload()

        self.assertIn({'id': chat.id, 'status': 'disabled'}, extra_users[1]['chats'], msg = f'the chat was not removed from user {extra_users[1]["id"]} - {extra_users[1]["nickName"]}')

        chats_service.remove_group_chat_participants(chat, users[0].id, [chat.participants[0]])

        expected_removal_result = {'id': users[0].id, 'isAdmin': False, 'status': 'disabled'}

        self.assertEqual(dict(chat.participants[0].to_mongo()), {**dict(chat.participants[0].to_mongo()), **expected_removal_result}, msg='The main admin user was not properly removed from the group')

        self.assertTrue(chat.participants[1].isAdmin, msg='The expected next admin in line for not promoted')

        chats_service.add_group_chat_participants(chat, users[1].id, [users[0]])

        self.assertIn({'id': chat.id, 'status': 'active'}, users[0]['chats'], msg = f'the chat was not removed from user {users[0]["id"]} - {users[0]["nickName"]}')

        self.assertFalse(chat.participants[0].isAdmin, msg='The returned admin user was returned as admin')

    def test_chat_participant_membership(self):

        users = self.create_users(self.users)

        chat = chats_service.create_chat('group', users[0].id, users, name="Test Group", icon_path="tests/resources/twitter_profile_image_size.jpeg")

        for participant in chat.participants:
            self.assertEqual(len(participant.membership), 1, msg=f'The participant {participant.nickName} membeship list should have a single entry')
            self.assertGreater(participant.membership[-1]['start'], chat.createdAt, msg=f'The participant {participant.nickName} membeship start should be greater then chat creation timestamp')
            self.assertLess(participant.membership[-1]['start'], datetime.utcnow(), msg=f'The participant {participant.nickName} membeship start should be less than {datetime.utcnow().timestamp()}')
            self.assertFalse(participant.membership[-1]['end'], msg=f'The participant {participant.nickName} membeship should not have end')

        chats_service.remove_group_chat_participants(chat, users[0].id, [chat.participants[1]])

        self.assertTrue(chat.participants[1].membership[-1]['end'], msg=f'The participant membeship should have end value')
        self.assertGreater(chat.participants[1].membership[-1]['end'], chat.participants[1].membership[-1]['start'], msg='The participant membeship end should be greater then membership start')

        chats_service.add_group_chat_participants(chat, users[0].id, [users[1]])
        self.assertEqual(len(chat.participants[1].membership), 2, msg='The participant membeship list should have a two entries')
        self.assertFalse(chat.participants[1].membership[-1]['end'], msg='The participant membeship should not have end value')
        self.assertGreater(chat.participants[1].membership[-1]['start'], chat.participants[1].membership[0]['end'], msg='The participant membeship last entry start should be greater then previous entry end')


# remove admin from group and then add him back
# add users to group chat
# remove users from group chat

