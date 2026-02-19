"""
Security module for JWT authentication and password hashing.
Provides token creation, validation, and password utilities.
"""
from datetime import datetime, timedelta, UTC
from typing import Optional
import hashlib
import hmac
import base64
import json
import logging
import os

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def _base64url_encode(data: bytes) -> str:
    """Base64url encode without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')


def _base64url_decode(data: str) -> bytes:
    """Base64url decode with padding restoration."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": int(expire.timestamp())})

    # Create JWT manually (header.payload.signature)
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(',', ':')).encode())
    payload_b64 = _base64url_encode(json.dumps(to_encode, separators=(',', ':')).encode())

    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        settings.secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{message}.{signature_b64}"


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts

        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            settings.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()

        actual_signature = _base64url_decode(signature_b64)
        if not hmac.compare_digest(expected_signature, actual_signature):
            return None

        # Decode payload
        payload = json.loads(_base64url_decode(payload_b64))

        # Check expiration
        if "exp" in payload:
            if datetime.now(UTC).timestamp() > payload["exp"]:
                return None

        return payload
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None


# Password hashing using PBKDF2 with SHA-256 (secure, stdlib-only)
# For higher security, consider using bcrypt or argon2-cffi
PBKDF2_ITERATIONS = 600000  # OWASP recommendation for SHA-256


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with random salt.
    Returns format: salt$hash (both hex-encoded)
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt,
        PBKDF2_ITERATIONS
    )
    return f"{salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its PBKDF2 hash."""
    try:
        salt_hex, key_hex = hashed_password.split('$')
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode(),
            salt,
            PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(expected_key, actual_key)
    except (ValueError, AttributeError):
        return False
