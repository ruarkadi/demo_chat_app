import mongoengine
import urllib
from chat.api import api
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('CHAT_APP_USERNAME')
password = os.getenv('CHAT_APP_PASSWORD')
db_name = os.getenv('CHAT_APP_DB_NAME')

mongoengine.connect(host=f"mongodb+srv://{username}:{urllib.parse.quote(password)}@{db_name}.uitqb.mongodb.net/chat?retryWrites=true&w=majority")

if __name__ == '__main__':
    api.run(port=5007)
