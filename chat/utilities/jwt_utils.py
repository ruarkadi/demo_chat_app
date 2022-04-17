import jwt
import datetime
from re import split

def create_jwt_token(data, secret, token_expiration_delta=60):
    payload = {
        "data": data,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=token_expiration_delta)
    }
    return jwt.encode(payload=payload, key=secret)

def decode_jwt_token(token, secret):
    return jwt.decode(token, key=secret, algorithms=['HS256'])

def get_token_from_header(auth_header):
    auth_header.strip().strip(",")
    header_type = "OTP"

    if not auth_header:
        return False

    field_values = split(r",\s*", auth_header)
    jwt_headers = [s for s in field_values if s.split()[0] == header_type]
    if len(jwt_headers) != 1:
        return False

    parts = jwt_headers[0].split()

    if len(parts) != 2:
        return False

    return parts[1]