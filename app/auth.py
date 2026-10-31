"""Password and security-answer hashing.

Values are stored as werkzeug hashes. A legacy plaintext value is still accepted once and then
re-saved as a hash, so older accounts upgrade themselves on their next login.
"""
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from app import db

_HASH_PREFIXES = ("scrypt:", "pbkdf2:")


def hash_secret(value):
    return generate_password_hash(value)


def verify_secret(record, attr, value):
    stored = getattr(record, attr)
    if stored.startswith(_HASH_PREFIXES):
        return check_password_hash(stored, value)
    if hmac.compare_digest(stored.encode(), value.encode()):
        setattr(record, attr, generate_password_hash(value))
        db.session.commit()
        return True
    return False
