from datetime import timedelta

from src.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_hash_password():
    password = "test-pass"
    hashed = hash_password(password)
    assert hashed != password


def test_verify_password():
    password = "test-pass"
    wrong_password = "123123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password(wrong_password, hashed) is False


def test_create_and_decode_token():
    email = "user@example.com"

    data = {"sub": email}
    token = create_access_token(data)
    assert token is not None

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == email
    assert "exp" in decoded


def test_decode_invalid_token():
    invalid_token = "invalid.token.123123"
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_token_expiration():
    email = "user@test.com"
    data = {"sub": email}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    decoded = decode_access_token(token)
    assert decoded is None