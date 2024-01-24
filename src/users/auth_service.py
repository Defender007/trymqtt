import jwt, datetime
from rest_framework.response import Response


def user_auth(req):
    token = req.COOKIES.get("jwt", None)
    if not token or token is None:
        return {"auth_error": "Unauthenticated!"}
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"auth_error": "Unauthenticated!"}
    return payload
