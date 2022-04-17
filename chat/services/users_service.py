from ..models.users_model import User
from ..utilities.mail_service import MailSender
from ..utilities import otp, utils
from ..utilities.exceptions import *

 # sign up
 # activate user
 # enable otp
 # disable
 # login
 # update settings
 # forgot password
 # delete user (user initidated)
 # disable user

 # sign up:
    # add pending user
    # send activation email

def signup(email, firstName, lastName, nickName, password, confirm_password, icon=None):

    if password != confirm_password:
        raise PasswordMismatch("password do not match")

    user = User.add_user(email, firstName, lastName, nickName, password, icon)

    MailSender.send_verification_email(user)

    return user

def verify_and_activate(user_id, verificationCode):

    user = User.get_user_by_id(user_id)

    if not user:
        raise UserNotExist("User does not exist")

    if user.state != "pending":
        raise UserStateError("User is already active or disabled")

    if user.verificationCode != verificationCode:
        raise ActivationCodeDoesNotMatchError("The provided activation code does not match the expected code")

    user.state = "active"
    del user.verificationCode

    user.save()

def login(email, password):
    user = User.get_user_by_email(email)

    if not user:
        raise UserNotExist("User does not exist")

    if user.state != "active":
        raise UserStateError("User is not active")

    is_pass_validated = user.validate_password(password)

    if not is_pass_validated:
        raise WrongCredentials("The credentials provided are wrong")

    if user.otp_key:
        return ( user, True )

    finish_login(user.id)

    return ( user, False )

def finish_login(user_id):
    user = User.get_user_by_id(user_id)
    user.updateLastLogin()
    user.save()

def configure_otp(user):

    user.update_otp_key()

    user.save()

    return otp.get_provisioning_uri(user.otp_key, user.email)

def validate_otp(user_id, totp_code):

    user = User.get_user_by_id(user_id)

    if not user:
        raise UserNotExist("User does not exist")

    return otp.validate_otp(totp_code, user.otp_key)

def update(user, **kwargs):

    user.firstName = kwargs['firstName'] if kwargs['firstName'] else user.firstName
    user.lastName = kwargs['lastName'] if kwargs['lastName'] else user.lastName
    user.nickName = kwargs['nickName'] if kwargs['nickName'] else user.nickName

    if kwargs['icon']:
        user.update_icon(kwargs['icon'])

    user.save()

    return user

def send_password_reset_code(email):

    user = User.get_user_by_email(email)

    if not user:
        raise UserNotExist("User does not exist")

    if user.state != "active":
        raise UserStateError("User is not active")

    user.update_verification_code()

    user.save()

    MailSender.send_verification_email(user, "forgotpass")

    return user

def verify_and_reset_password(email, password, confirm_password, verificationCode):

    user = User.get_user_by_email(email)

    if not user:
        raise UserNotExist("User does not exist")

    if user.state != "active":
        raise UserStateError("User is not active")

    if user.verificationCode != verificationCode:
        raise ActivationCodeDoesNotMatchError("The provided activation code does not match the expected code")

    if password != confirm_password:
        raise PasswordMismatch("password do not match")

    user.update_password(password)

    del user.verificationCode

    user.save()

    return user

def delete_user(user):

    # TODO:

    user.update_password(utils.generate_complex_random_string())

    user.state = "disabled"

    user.save()

def activate_user(user):

    user.state = "active"

    user.save()

def update_last_seen(user):

    user.updateLastActive()
    user.save()