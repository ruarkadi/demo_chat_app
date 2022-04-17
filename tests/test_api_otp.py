import time
from flask import app
from chat.api import api
import mongoengine
import unittest
import mongomock
import json
import bson
from chat.models.users_model import User
from chat.models.chats_model import Chat
from chat.services import chats_service
from chat.utilities import encryption, otp, jwt_utils
from chat.services import users_service
from .utils.mock_totp import get_totp_token



class test_login(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = mongoengine.connect('test', host='mongomock://localhost')
        cls.db = cls.connection['test']
        cls.users_collection = cls.db['users']
        api.testing = True

    def setUp(self):
        self.insert_user_to_db()
        return super().setUp()

    @classmethod
    def tearDownClass(cls):
        mongoengine.disconnect()

    def tearDown(self) -> None:
        self.connection.drop_database('test')
        return super().tearDown()

    def insert_user_to_db(self):

        user_salt = encryption.generate_salt()
        user_encrypted_pass = encryption.encrypt("Testing!2", user_salt)
        password = user_salt + user_encrypted_pass
        otp_key = otp.get_secret_key()


        self.users_collection.insert_one(
            {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user15@gmail.com",
                "nickName": "Enzane15",
                "password": password,
                "state": "active",
                "otp_key": otp_key
            }
        )

    def test_api_successful_otp_login(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, api.config['JWT_OTP_SECRET'])
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code={token}",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(200, result.status_code)
            self.assertTrue(result.json['success'])
            self.assertTrue(result.json['access_token'])

    def test_api_failed_otp_login_non_existent_user_in_auth_token(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(bson.ObjectId())}, api.config['JWT_OTP_SECRET'])
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code={token}",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(404, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_otp_login_bad_secret_in_auth_token(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, "harta")
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code={token}",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(422, result.status_code)

    def test_api_failed_otp_login_malstructured_auth_token(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, "harta")
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code={token}",
                headers={'Authorization': f"BEAR {auth_token}"}
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_otp_bad_otp_code(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, api.config['JWT_OTP_SECRET'])
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code=758094",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])


    def test_api_failed_otp_request_validation(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, api.config['JWT_OTP_SECRET'])
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code=",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/otp",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/otp?code={token}",
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])


    def test_api_failed_otp_login_expired_otp_auth_token(self):
        with api.test_client() as client:

            user = self.users_collection.find_one({"email" : "test.user15@gmail.com"})
            auth_token = jwt_utils.create_jwt_token({"user_id": str(user['_id'])}, api.config['JWT_OTP_SECRET'], -1)
            token = get_totp_token(user['otp_key'])

            result = client.get(
                f"/auth/otp?code={token}",
                headers={'Authorization': f"OTP {auth_token}"}
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])
