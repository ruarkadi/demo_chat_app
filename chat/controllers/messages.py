from ..services import messages_service
from ..services import chats_service
from flask import Flask, json, jsonify, request, Response
from ..api.server import api
from ..utilities.utils import build_api_response_data
from ..utilities.exceptions import *
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required

@api.route("/chats/<chat_id>/messages", methods=['POST'])
@jwt_required()
def send_message(chat_id):

    message = messages_service.send_message(chat_id, current_user.id, request.json['text'], request.json['attachement_type'], request.json.get('attachement_path'))

    return build_api_response_data(message, True), 200

@api.route("/chats/<chat_id>/messages", methods=['GET'])
@jwt_required()
def get_messages(chat_id):

    timestamp = request.args.get('from_timestamp')

    messages = messages_service.get_messages(chat_id, current_user.id, timestamp)

    return build_api_response_data(messages, True), 200
