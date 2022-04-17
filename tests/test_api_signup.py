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



class test_signup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = mongoengine.connect('test', host='mongomock://localhost')
        cls.db = cls.connection['test']
        cls.users_collection = cls.db['users']
        api.testing = True

    @classmethod
    def tearDownClass(cls):
        mongoengine.disconnect()

    def tearDown(self) -> None:
        self.connection.drop_database('test')
        return super().tearDown()

    def test_api_successful_signup(self):
        with api.test_client() as client:

            sent = {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user13@gmail.com",
                "nickName": "Enzane13",
                "password": "Testing!2",
                "confirm_password": "Testing!2"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(201, result.status_code)
            self.assertTrue(result.json['success'])
            self.assertTrue(bson.ObjectId.is_valid(result.json['data']))

    def test_api_failed_signup_missing_field(self):
        with api.test_client() as client:

            sent = {
                "lastName": "ruditzky",
                "email": "test.user13@gmail.com",
                "nickName": "Enzane13",
                "password": "Testing!2",
                "confirm_password": "Testing!2"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_signup_wrong_email(self):
        with api.test_client() as client:

            sent = {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user13",
                "nickName": "Enzane13",
                "password": "Testing!2",
                "confirm_password": "Testing!2"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_signup_user_exists(self):
        with api.test_client() as client:

            self.users_collection.insert_one(
                {
                    "firstName": "arkadi",
                    "lastName": "ruditzky",
                    "email": "test.user15@gmail.com",
                    "nickName": "Enzane15",
                    "password": "Testing!2",
                    "confirm_password": "Testing!2"
                }
            )

            sent = {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user15@gmail.com",
                "nickName": "Enzane15",
                "password": "Testing!2",
                "confirm_password": "Testing!2"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_signup_password_mismatch(self):
        with api.test_client() as client:

            sent = {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user13@gmail.com",
                "nickName": "Enzane13",
                "password": "Testing!2",
                "confirm_password": "Testing!3"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(406, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_signup_password_strength_error(self):
        with api.test_client() as client:

            sent = {
                "firstName": "arkadi",
                "lastName": "ruditzky",
                "email": "test.user13@gmail.com",
                "nickName": "Enzane13",
                "password": "abcd",
                "confirm_password": "abcd"
            }

            result = client.post(
                '/auth/register',
                json=sent,
            )

            self.assertEqual(406, result.status_code)
            self.assertFalse(result.json['success'])
