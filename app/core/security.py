"""
보안 모듈 - JWT 인증 및 비밀번호 해싱

외부 라이브러리(PyJWT, bcrypt) 없이 표준 라이브러리만 사용하여 구현.
- JWT: 수동으로 header.payload.signature 구조 생성 (HS256 알고리즘)
- 비밀번호: PBKDF2-HMAC-SHA256 해싱 (OWASP 권장 60만 회 반복)
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
    """
    Base64url 인코딩 (패딩 제거).
    JWT 표준에서는 URL-safe Base64를 사용하며 '=' 패딩을 제거함.
    """
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _base64url_decode(data: str) -> bytes:
    """
    Base64url 디코딩 (패딩 복원).
    인코딩 시 제거된 패딩을 4의 배수가 되도록 복원 후 디코딩.
    """
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
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
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": int(expire.timestamp())})

    # Create JWT manually (header.payload.signature)
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = _base64url_encode(
        json.dumps(to_encode, separators=(",", ":")).encode()
    )

    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        settings.secret_key.encode(), message.encode(), hashlib.sha256
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
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts

        # 서명 검증: header.payload를 SECRET_KEY로 HMAC-SHA256 해싱하여 비교
        # compare_digest를 사용하여 타이밍 공격(timing attack) 방지
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            settings.secret_key.encode(), message.encode(), hashlib.sha256
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


# PBKDF2-SHA256 비밀번호 해싱 (표준 라이브러리만 사용)
# 반복 횟수: OWASP 2023 권장 기준 (SHA-256의 경우 60만 회)
# 더 강력한 보안이 필요하면 bcrypt 또는 argon2-cffi 사용 고려
PBKDF2_ITERATIONS = 600000


def hash_password(password: str) -> str:
    """
    비밀번호 해싱 (PBKDF2-HMAC-SHA256).

    저장 형식: "salt$hash" (둘 다 hex 인코딩)
    - salt: 32바이트 무작위 값 (레인보우 테이블 공격 방지)
    - hash: 비밀번호 + salt를 60만 회 반복 해싱한 결과
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"{salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증.

    저장된 salt를 추출하여 입력 비밀번호를 동일하게 해싱한 후 비교.
    compare_digest를 사용하여 타이밍 공격 방지.
    """
    try:
        salt_hex, key_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode(), salt, PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(expected_key, actual_key)
    except (ValueError, AttributeError):
        return False
