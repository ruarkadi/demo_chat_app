from ..services import chats_service, users_service
from flask import Flask, json, jsonify, request, Response
from ..api.server import api
from ..api.responses import response_filters
from ..utilities.utils import build_api_response_data
from ..utilities.exceptions import *
from ..utilities.jwt_utils import decode_jwt_token, create_jwt_token, get_token_from_header
from jwt.exceptions import ExpiredSignatureError
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required
import json

@api.route("/chats", methods=['GET'])
@jwt_required()
def get_chats():
    chats = chats_service.get_chats_by_user(current_user)

    return build_api_response_data(chats, True), 200

@api.route("/chats", methods=['POST'])
@jwt_required()
def create_chat():
    if "icon" not in request.json:
        request.json["icon"] = None

    if request.json['chat_type'] == "private":
        request.json['name'] = None

    chat = chats_service.create_chat(
        request.json['chat_type'],
        current_user['id'],
        request.json['participant_ids'],
        request.json['name'],
        request.json['icon']
    )

    return build_api_response_data(chat['id'], True), 201


@api.route("/chats/<chat_id>", methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    chat = chats_service.get_chat(chat_id, current_user.id)

    return build_api_response_data(chat, True), 200


@api.route("/chats/<chat_id>", methods=['PUT'])
@jwt_required()
def update_chat(chat_id):
    if "icon_path" not in request.json:
        request.json["icon_path"] = None

    if "name" not in request.json:
        request.json['name'] = None

    chat = chats_service.update_chat(chat_id, current_user.id, name=str(request.json['name']), icon_path=request.json["icon_path"])

    return build_api_response_data(chat, True), 200



