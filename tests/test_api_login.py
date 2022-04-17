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
from chat.utilities import encryption



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

        self.users_collection.insert_one(
            {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user15@gmail.com",
                "nickName": "Enzane15",
                "password": password,
                "state": "active",
            }
        )

    def test_api_successful_login(self):
        with api.test_client() as client:
            sent = {
                "email": "test.user15@gmail.com",
                "password": "Testing!2",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(200, result.status_code)
            self.assertTrue(result.json['success'])
            self.assertTrue(result.json['access_token'])

    def test_api_bad_password_login(self):
        with api.test_client() as client:
            sent = {
                "email": "test.user15@gmail.com",
                "password": "Testing!3",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(401, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_bad_email_login(self):
        with api.test_client() as client:
            sent = {
                "email": "test.user14@gmail.com",
                "password": "Testing!2",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(404, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_wrong_user_state_login(self):
        with api.test_client() as client:
            self.users_collection.update_one(
                {
                    "email": 'test.user15@gmail.com'
                },
                {
                    '$set': {
                        'state': 'inactive'
                    }
                },
                upsert=False
            )

            sent = {
                "email": "test.user15@gmail.com",
                "password": "Testing!2",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(405, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_bad_validation_login(self):
        with api.test_client() as client:
            sent = {
                "email": "test.user15@gmail.com",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

            sent = {
                "password": "Testing!2",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_otp_user_login(self):
        with api.test_client() as client:
            self.users_collection.update_one(
                {
                    "email": 'test.user15@gmail.com'
                },
                {
                    '$set': {
                        'otp_key': 'sjjflslllf;ll'
                    }
                },
                upsert=False
            )

            sent = {
                "email": "test.user15@gmail.com",
                "password": "Testing!2",
            }

            result = client.post(
                '/auth/login',
                json=sent,
            )

            self.assertEqual(200, result.status_code)
            self.assertTrue(result.json['success'])
            self.assertTrue(result.json['otp_token'])