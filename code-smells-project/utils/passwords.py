import hashlib
import hmac
import os

_ITERATIONS = 260_000


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    if not stored or not stored.startswith("pbkdf2_sha256$"):
        return hmac.compare_digest(password or "", stored or "")
    _, iterations, salt_hex, digest_hex = stored.split("$", 3)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        (password or "").encode(),
        bytes.fromhex(salt_hex),
        int(iterations),
    )
    return hmac.compare_digest(digest.hex(), digest_hex)
