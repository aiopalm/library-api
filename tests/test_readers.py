import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "user@mail.ru", "password": "test-pass"}
    )
    response = await client.post(
        "/auth/login",
        data={"username": "user@mail.ru", "password": "test-pass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_reader(client: AsyncClient, auth_headers):
    response = await client.post(
        "/readers/",
        json={"name": "Ivan", "email": "reader@mail.ru"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Ivan"


async def test_create_reader_without_auth(client: AsyncClient):
    response = await client.post(
        "/readers/",
        json={"name": "Ivan", "email": "reader@mail.ru"}
    )
    assert response.status_code == 401
