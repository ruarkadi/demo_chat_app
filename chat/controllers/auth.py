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

@api.route('/auth/register', methods=['POST'])
def signup():
    if "icon" not in request.json:
        request.json["icon"] = None
    user = users_service.signup(
        request.json['email'],
        request.json['firstName'],
        request.json['lastName'],
        request.json['nickName'],
        request.json['password'],
        request.json['confirm_password'],
        request.json['icon']
    )

    return build_api_response_data(user.id, True), 201

@api.route("/auth/activate", methods=['GET'])
def user_activation():
    code = request.args.get('code')
    id = request.args.get('id')

    users_service.verify_and_activate(id, code)

    return build_api_response_data("", True), 200

@api.route("/auth/login", methods=['POST'])
def user_login():
    user, is_otp = users_service.login(
        request.json['email'],
        request.json['password']
    )

    if is_otp:

        access_token = create_jwt_token({"user_id": str(user.id)}, api.config['JWT_OTP_SECRET'])

        return build_api_response_data(access_token, True, "otp_token"), 200

    access_token = create_access_token(identity=user.id)

    return build_api_response_data(access_token, True, "access_token"), 200

@api.route("/auth/otp", methods=['GET'])
def verify_otp():
    otp_code = request.args.get('code')
    auth_header = request.headers.get("Authorization", "")

    otp_token = get_token_from_header(auth_header)

    if not otp_token:
        raise BadAuthorizationHeaderError("Bad authorization header")

    try:
        decoded_payload = decode_jwt_token(otp_token, api.config['JWT_OTP_SECRET'])
    except ExpiredSignatureError:
        raise ExpiredAuthTokenError("Signature has expired")

    user_id = decoded_payload['data']['user_id']

    if not users_service.validate_otp(user_id, otp_code):
        raise WrongOTPCodeError("Invalid OTP code")

    users_service.finish_login(user_id)
    access_token = create_access_token(identity=user_id)
    return build_api_response_data(access_token, True, "access_token"), 200

@api.route("/auth/forgot-password", methods=['POST'])
def forgot_password():

    users_service.send_password_reset_code(request.json['email'])

    return build_api_response_data("", True), 200

@api.route("/auth/change-password", methods=['GET'])
@jwt_required()
def change_password():

    users_service.send_password_reset_code(current_user.email)

    return build_api_response_data("", True), 200


@api.route("/auth/set-password", methods=['POST'])
def set_password():

    code = request.args.get('code')
    email = request.args.get('email')

    users_service.verify_and_reset_password(email, request.json['password'], request.json['confirm_password'], code)

    return build_api_response_data("", True), 200
