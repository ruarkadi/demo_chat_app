import hashlib
import os

def generate_salt():
    return os.urandom(32)

def encrypt(string, salt):
    return hashlib.pbkdf2_hmac('sha256', string.encode('utf-8'), salt, 100000)

def validate(string, encrypted_string, salt):
    return encrypted_string == encrypt(string, salt)