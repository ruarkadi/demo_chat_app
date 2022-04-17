from ..services import chats_service
from flask import Flask, json, jsonify, request, Response
from ..api.server import api
from ..utilities.utils import build_api_response_data
from ..utilities.exceptions import *
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required

@api.route("/chats/<chat_id>/participants/bulkAdd", methods=['PUT'])
@jwt_required()
def bulk_add_participants(chat_id):

    participants = chats_service.add_group_chat_participants(chat_id, current_user.id, request.json['user_ids'])

    return build_api_response_data(participants, True), 200

@api.route("/chats/<chat_id>/participants/bulkRemove", methods=['PUT'])
@jwt_required()
def bulk_remove_participants(chat_id):

    participants = chats_service.remove_group_chat_participants(chat_id, current_user.id, request.json['participant_ids'])

    return build_api_response_data(participants, True), 200

@api.route("/chats/<chat_id>/participants/bulkMakeAdmins", methods=['PUT'])
@jwt_required()
def bulk_participants_make_admins(chat_id):

    participants = chats_service.change_users_role(chat_id, current_user.id, request.json['participant_ids'], admin_status=True)

    return build_api_response_data(participants, True), 200

@api.route("/chats/<chat_id>/participants/bulkRemoveAdmins", methods=['PUT'])
@jwt_required()
def bulk_participants_remove_admins(chat_id):

    participants = chats_service.change_users_role(chat_id, current_user.id, request.json['participant_ids'])

    return build_api_response_data(participants, True), 200

@api.route("/chats/<chat_id>/participants/remove", methods=['DELETE'])
@jwt_required()
def leave_chat(chat_id):

    chats_service.leave_group_chat(chat_id, current_user.id)

    return build_api_response_data("", True), 200