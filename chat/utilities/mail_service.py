from mailjet_rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

class MailSender():

    api_key = os.getenv('CHAT_APP_MAILJET_API_KEY')
    api_secret = os.getenv('CHAT_APP_MAILJET_API_SECRET')

    @staticmethod
    def send_email(mail_from, mail_to, mail_subject, mail_text):
        mailjet = Client(auth=(MailSender.api_key, MailSender.api_secret), version='v3.1')
        data = {
            'Messages': [
                {
                    "From": mail_from,
                    "To": [ mail_to ],
                    "Subject": mail_subject,
                    "TextPart": mail_text
                }
            ]
        }

        result = mailjet.send.create(data=data)

        return True if result.status_code < 400 else False

    @staticmethod
    def send_verification_email(user, verification_type="activation"):
        email_from = {
            "Email": f"activation@{os.getenv('CHAT_APP_MAILJET_DOMAIN')}",
            "Name": "ChatApp Account Activation"
        }
        email_to = {
            "Email": user.email,
            "Name": user.firstName + " " + user.lastName
        }
        if verification_type == "activation":
            subject = "ChatApp Account Activation"

            textPart = f"Hello compadre, please activate your accounte by typing in the following code into the app: { user.verificationCode }"

        if verification_type == "forgotpass":
            subject = "ChatApp Forgot Password"

            textPart = f"Hello compadre, please type the following code into the app: { user.verificationCode } to proceed with password reset"

        return MailSender.send_email(email_from, email_to, subject, textPart)


