import jwt, datetime
from rest_framework.response import Response


def user_auth(req):
    token = req.COOKIES.get("jwt")
    if not token:
        return {"auth_error": "Unauthenticated!"}
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"auth_error": "Unauthenticated!"}
    return payload
