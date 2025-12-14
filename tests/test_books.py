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


async def test_create_book(client: AsyncClient, auth_headers):
    response = await client.post(
        "/books/",
        json={
            "title": "Book",
            "author": "Author",
            "year": 2024,
            "isbn": "978-3-16-148410-0",
            "copies_available": 5
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Book"


async def test_create_book_without_auth(client: AsyncClient):
    response = await client.post(
        "/books/",
        json={
            "title": "Book",
            "author": "Author",
            "year": 2024,
            "isbn": "978-3-16-148410-0",
            "copies_available": 5
        }
    )
    assert response.status_code == 401


async def test_get_all_books(client: AsyncClient, auth_headers):
    await client.post(
        "/books/",
        json={
            "title": "Book",
            "author": "Author",
            "year": 2024,
            "isbn": "978-3-16-148410-0",
            "copies_available": 5
        },
        headers=auth_headers
    )

    response = await client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()["books"]) == 1
