from flask import Flask
from flask_jwt_extended import JWTManager
import datetime
from dotenv import load_dotenv
import os

api = Flask(__name__)

load_dotenv()

api.config["JWT_SECRET_KEY"] = os.getenv("CHAT_APP_JWT_SECRET_KEY")
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(weeks=4) #Change this!
api.config["JWT_OTP_SECRET"] = os.getenv('CHAT_APP_JWT_OTP_SECRET')
jwt = JWTManager(api)

from .hooks import *
from .error_handler import *
from ..controllers.auth import *
from ..controllers.chats import *
from ..controllers.messages import *
from ..controllers.participants import *
from ..controllers.users import *