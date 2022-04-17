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

            self.users_collection.insert_one(
                {
                    "firstName": "arkadi",
                    "lastName": "ruditzky",
                    "email": "test.user15@gmail.com",
                    "nickName": "Enzane15",
                    "password": b"Testing!2",
                    "state": "pending",
                    "verificationCode": "AHAHA",
                }
            )

            ts = self.users_collection.find_one({"nickName": "Enzane15"})
            result = client.get(
                f"/auth/activate?code=AHAHA&id={str(ts['_id'])}"
            )
            self.assertEqual(200, result.status_code)
            self.assertTrue(result.json['success'])

    def test_api_failed_signup_wrong_id(self):
        with api.test_client() as client:

            fake_id = bson.ObjectId()

            self.users_collection.insert_one(
                {
                    "firstName": "arkadi",
                    "lastName": "ruditzky",
                    "email": "test.user15@gmail.com",
                    "nickName": "Enzane15",
                    "password": b"Testing!2",
                    "state": "pending",
                    "verificationCode": "AHAHA",
                }
            )

            result = client.get(
                f"/auth/activate?code=AHAHA&id={str(fake_id)}"
            )
            self.assertEqual(404, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/activate?code=AHAHA&id=asdkjljsf"
            )
            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/activate?code=AHAHA"
            )
            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/activate?code=AHAHA&id"
            )
            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

    def test_api_failed_signup_wrong_code(self):
        with api.test_client() as client:

            self.users_collection.insert_one(
                {
                    "firstName": "arkadi",
                    "lastName": "ruditzky",
                    "email": "test.user15@gmail.com",
                    "nickName": "Enzane15",
                    "password": b"Testing!2",
                    "state": "pending",
                    "verificationCode": "AHAHA",
                }
            )

            ts = self.users_collection.find_one({"nickName": "Enzane15"})
            result = client.get(
                f"/auth/activate?code=AHDHA&id={str(ts['_id'])}"
            )
            self.assertEqual(418, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/activate?id={str(ts['_id'])}&code="
            )
            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])

            result = client.get(
                f"/auth/activate?id={str(ts['_id'])}"
            )
            self.assertEqual(400, result.status_code)
            self.assertFalse(result.json['success'])
