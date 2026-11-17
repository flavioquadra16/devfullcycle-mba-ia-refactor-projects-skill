import hashlib
import hmac

from config.settings import settings


def issue_token(user_id):
    payload = str(user_id)
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"{payload}.{signature}"
