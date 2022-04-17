from ..services import chats_service, users_service
from flask import Flask, json, jsonify, request, Response
from ..api.server import api
from ..utilities.utils import build_api_response_data
from ..utilities.exceptions import *
from ..utilities.jwt_utils import decode_jwt_token, create_jwt_token, get_token_from_header
from jwt.exceptions import ExpiredSignatureError
from flask_jwt_extended import create_access_token
from flask_jwt_extended import current_user
from flask_jwt_extended import jwt_required


@api.route('/users/me', methods=['PUT'])
@jwt_required()
def update_user():

    request.json['icon'] = request.json.get('icon', None)
    request.json['firstName'] = request.json.get('firstName', None)
    request.json['lastName'] = request.json.get('lastName', None)
    request.json['nickName'] = request.json.get('nickName', None)

    user = users_service.update(
        current_user,
        **request.json
    )

    return build_api_response_data(user, True), 200


@api.route('/users/me', methods=['DELETE'])
@jwt_required()
def delete_user():

    chats = chats_service.get_chats_by_user(current_user)

    chats_service.leave_group_chats(current_user, chats)

    chats_service.reset_participant_membership_in_chats(chats, current_user.id)

    users_service.delete_user(current_user)

    return build_api_response_data("", True), 200

