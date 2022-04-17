from flask import request

validation_schemas = {
    '/auth/register': {
        'POST': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "minLength": 1
                    },
                    "firstName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "lastName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "nickName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "password": {
                        "type": "string",
                        "minLength": 1
                    },
                    "confirm_password": {
                        "type": "string",
                        "minLength": 1
                    },
                    "icon": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["email", "firstName", "lastName", "nickName", "password", "confirm_password"]
            }
        }
    },
    '/auth/activate': {
        'GET': {
            "validation_data_func": (lambda: {"id": request.args.get('id'), "code": request.args.get('code')}),
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "minLength": 1
                    },
                    "id": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["code", "id"]
            }
        }
    },
    '/auth/login': {
        'POST': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "minLength": 1
                    },
                    "password": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["email", "password"]
            }
        }
    },
    '/auth/me': {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {}
        }
    },
    '/auth/otp': {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {
                "type": "object",
                "properties": {
                    "otp_code": {
                        "type": "int",
                        "minLength": 1
                    },
                },
                "required": ["otp_code"]
            }
        }
    },
    '/auth/forgot-password': {
        'POST': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "minLength": 1
                    },
                },
                "required": ["email"]
            }
        }
    },
    '/auth/set-password': {
        'POST': {
            "validation_data_func": (lambda: {**{"email": request.args.get('email'), "code": request.args.get('code')}, **request.json}),
            "schema": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "minLength": 1
                    },
                    "email": {
                        "type": "string",
                        "minLength": 1
                    },
                    "password": {
                        "type": "string",
                        "minLength": 1
                    },
                    "confirm_password": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["code", "email", "password", "confirm_password"]
            }
        }
    },
    '/auth/change-password': {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {}
        }
    },
    '/chats': {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {}
        },
        'POST': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "chat_type": {
                        "enum": ["private", "group"]
                    },
                    "participant_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 24,
                            "maxLength": 24
                        },
                        "minItems": 2,
                        "uniqueItems": True
                    },
                    "name": {
                        "type": "string",
                        "minLength": 1
                    },
                    "icon": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ["chat_type", "participant_ids"]
            }
        }
    },
    "/chats/<chat_id>": {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {}
        },
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1
                    },
                    "icon_path": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": []
            }
        }
    },
    "/chats/<chat_id>/participants/bulkAdd": {
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 24,
                            "maxLength": 24
                        },
                        "minItems": 1,
                        "uniqueItems": True
                    }
                },
                "required": ['user_ids']
            }
        }
    },
    "/chats/<chat_id>/participants/bulkRemove": {
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "participant_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 24,
                            "maxLength": 24
                        },
                        "minItems": 1,
                        "uniqueItems": True
                    }
                },
                "required": ['participant_ids']
            }
        }
    },
    "/chats/<chat_id>/participants/bulkMakeAdmins": {
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "participant_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 24,
                            "maxLength": 24
                        },
                        "minItems": 1,
                        "uniqueItems": True
                    }
                },
                "required": ['participant_ids']
            }
        }
    },
    "/chats/<chat_id>/participants/bulkRemoveAdmins": {
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "participant_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 24,
                            "maxLength": 24
                        },
                        "minItems": 1,
                        "uniqueItems": True
                    }
                },
                "required": ['participant_ids']
            }
        }
    },
    "/chats/<chat_id>/messages": {
        'GET': {
            "validation_data_func": (lambda: None),
            "schema": {}
        },
        'POST': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "minLength": 1
                    },
                    "attachement_type": {
                        "enum": ["text", "image", "video"]
                    },
                    "attachement_path": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": ['text', 'attachement_type']
            }
        }
    },
    "/users/me": {
        'PUT': {
            "validation_data_func": (lambda: request.json),
            "schema": {
                "type": "object",
                "properties": {
                    "firstName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "lastName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "nickName": {
                        "type": "string",
                        "minLength": 1
                    },
                    "icon": {
                        "type": "string",
                        "minLength": 1
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        }
    }
}
