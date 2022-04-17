import pyotp

def get_secret_key():
    return pyotp.random_base32()

def get_provisioning_uri(secret, email, issuer_name="Chat App"):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

def validate_otp(totp_code, secret):
    totp = pyotp.TOTP(secret)
    return totp.verify(totp_code)