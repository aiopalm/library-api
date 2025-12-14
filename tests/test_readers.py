import pytest
from httpx import AsyncClient


@pytest.fixture
async def auth_headers(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": "artem@mail.ru", "password": "test-pass"}
    )
    response = await client.post(
        "/auth/login",
        json={"email": "artem@mail.ru", "password": "test-pass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_reader(client: AsyncClient, auth_headers):
    response = await client.post(
        "/readers/",
        json={"name": "Nikita", "email": "nikita@mail.ru"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Nikita"


async def test_create_reader_without_auth(client: AsyncClient):
    response = await client.post(
        "/readers/",
        json={"name": "Artem", "email": "artem@mail.ru"}
    )
    assert response.status_code == 401
