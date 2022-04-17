class PasswordMismatch(Exception):
    pass

class WrongCredentials(Exception):
    pass

class PasswordStrengthError(Exception):
    pass

class UserChatPermissionsError(Exception):
    pass

class UserMessageDeletePermissionsError(Exception):
    pass

class ActivationCodeDoesNotMatchError(Exception):
    pass

class NotExistError(Exception):
    pass

class ChatNotExistError(NotExistError):
    pass

class UserNotExist(NotExistError):
    pass

class UserNotExistInChatError(NotExistError):
    pass

class UserStateError(Exception):
    pass

class BadAuthorizationHeaderError(Exception):
    pass

class WrongOTPCodeError(Exception):
    pass

class ExpiredAuthTokenError(Exception):
    pass

class ChatAlreadyExists(Exception):
    pass

class MissingArg(Exception):
    pass

class ChatValidationError(Exception):
    pass

class ParticipantsNotExit(NotExistError):
    pass

class ParticipantNotExit(NotExistError):
    pass

class MessageNotExit(NotExistError):
    pass
# raise Exception("A name is required")
# raise Exception("Private chat can only contain two participants")
# raise Exception("Private chat already exists")
# raise Exception("Private chats cannot have a custom icon")
# raise TypeError("The sender was not a user")
# raise TypeError("The text field is not a str")
# raise Exception(err)


# raise PasswordStrengthError(password_errors)


# raise Exception('The requesting user does not exist')
# raise Exception('The requesting user is not in the users list provided')


# raise UserChatPermissionsError('The user does not have permissions on the chat')
# raise UserChatPermissionsError('The user does not have permissions on the chat')
# raise UserChatPermissionsError('The user does not have permissions on the chat')
# raise UserChatPermissionsError('The user does not have permissions on the chat')
# raise UserChatPermissionsError('The user does not have permissions on the chat')


# raise Exception('The user can\'t change his own role')
# raise Exception('The chat does not exist')
# raise Exception('The user was never a chat participant')
# raise Exception("The sender needs to be a participant in the chat")
# raise Exception('Message not found')
# raise Exception("The user needs to be a participant in the chat")
# raise UserMessageDeletePermissionsError("User can only delete own messages")
# raise PasswordMismatch("password do not match")
# raise Exception("Activation code does not match")
# raise Exception("User does not exist")
# raise Exception("User is not active")
# raise Exception("Password does not match")
# raise Exception("User does not exist")
# raise Exception("User is not active")
# raise Exception("password do not match")
# raise Exception("The existing password does not match")
# raise Exception("passwords do not match")
# raise Exception("User is not active")
# raise Exception("Private chat already exists")
# raise Exception("Private chat can only contain two participants")
# raise Exception("A name is required")
# raise TypeError("The sender was not a user")
# raise FileNotFoundError("File not found in specified path")
