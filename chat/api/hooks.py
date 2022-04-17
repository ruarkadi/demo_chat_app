from os import abort
from flask import Flask, json, jsonify, request, Response, abort
from .requests import validate_request_input, validation_schemas
from .server import api, jwt
from ..models.users_model import User


@api.before_request
def validate_json_schema_exist():
    if str(request.url_rule) not in validation_schemas:
        abort(Response('Missing validation schema for route', status=404))

@api.before_request
def validate():
    validate_request_input(str(request.url_rule), request.method)

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return str(user_id)

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.get_user_by_id(identity)