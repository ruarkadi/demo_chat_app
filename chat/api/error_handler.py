import mongoengine
from flask import Flask, json, jsonify, request, Response
import jsonschema
import traceback

from ..utilities.exceptions import *
from .server import api
from ..utilities.utils import build_api_response_data

@api.errorhandler(Exception)
def error_handling(e):
    if isinstance(e, jsonschema.exceptions.ValidationError):
        return build_api_response_data(e.message, False), 400

    elif isinstance(e, mongoengine.errors.ValidationError):
        if list(e.to_dict().values()):
            error_msg=list(e.to_dict().values())[0]
        else:
            error_msg=e.__str__()
        return build_api_response_data(error_msg, False), 400

    elif isinstance(e, mongoengine.errors.NotUniqueError):
        error_msg = "already exists"
        if e.__context__.details:
            error_msg=list(e.__context__.details['keyPattern'].keys())[0] + " " + error_msg
        return build_api_response_data(error_msg, False), 400

    elif isinstance(e, NotExistError):
        return build_api_response_data(e.__str__(), False), 404

    elif isinstance(e, ActivationCodeDoesNotMatchError):
        return build_api_response_data(e.__str__(), False), 418

    elif isinstance(e, UserStateError):
        return build_api_response_data(e.__str__(), False), 405

    elif isinstance(e, PasswordStrengthError):
        return build_api_response_data(e.__str__(), False), 406

    elif isinstance(e, PasswordMismatch):
        return build_api_response_data(e.__str__(), False), 406

    elif isinstance(e, WrongCredentials):
        return build_api_response_data(e.__str__(), False), 401

    elif isinstance(e, BadAuthorizationHeaderError):
        return build_api_response_data(e.__str__(), False), 401

    elif isinstance(e, WrongOTPCodeError):
        return build_api_response_data(e.__str__(), False), 401

    elif isinstance(e, ExpiredAuthTokenError):
        return build_api_response_data(e.__str__(), False), 401

    elif isinstance(e, ChatValidationError):
        return build_api_response_data(e.__str__(), False), 406

    elif isinstance(e, MissingArg):
        return build_api_response_data(e.__str__(), False), 406

    elif isinstance(e, ChatAlreadyExists):
        return build_api_response_data(e.__str__(), False), 409




    # We return e if no defines error were caught to propagate server errors as is instead of overwriting them
    # return e
    else:
        return build_api_response_data(e.__str__(), False), 500
