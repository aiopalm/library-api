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


@pytest.fixture
async def setup_book_and_reader(client: AsyncClient, auth_headers):
    book_response = await client.post(
        "/books/",
        json={
            "title": "Book",
            "author": "Author",
            "year": 2024,
            "isbn": "978-3-16-148410-0",
            "copies_available": 3
        },
        headers=auth_headers
    )

    reader_response = await client.post(
        "/readers/",
        json={"name": "Ivan", "email": "ivan@mail.ru"},
        headers=auth_headers
    )

    return {
        "book_id": book_response.json()["id"],
        "reader_id": reader_response.json()["id"]
    }


async def test_borrow_book(client: AsyncClient, auth_headers, setup_book_and_reader):
    response = await client.post(
        "/borrowing/borrow",
        json={
            "book_id": setup_book_and_reader["book_id"],
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["return_date"] is None


async def test_borrow_decreases_copies(client: AsyncClient, auth_headers, setup_book_and_reader):
    book_id = setup_book_and_reader["book_id"]

    book_before = await client.get(f"/books/{book_id}")
    initial_copies = book_before.json()["copies_available"]

    await client.post(
        "/borrowing/borrow",
        json={
            "book_id": book_id,
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )

    book_after = await client.get(f"/books/{book_id}")
    assert book_after.json()["copies_available"] == initial_copies - 1


async def test_cannot_borrow_without_copies(client: AsyncClient, auth_headers):
    book_response = await client.post(
        "/books/",
        json={
            "title": "Book",
            "author": "Author",
            "year": 2024,
            "isbn": "978-3-16-148410-1",
            "copies_available": 0
        },
        headers=auth_headers
    )

    reader_response = await client.post(
        "/readers/",
        json={"name": "Grisha", "email": "grisha@mail.ru"},
        headers=auth_headers
    )

    response = await client.post(
        "/borrowing/borrow",
        json={
            "book_id": book_response.json()["id"],
            "reader_id": reader_response.json()["id"]
        },
        headers=auth_headers
    )
    assert response.status_code == 400


async def test_limit_three_books(client: AsyncClient, auth_headers):
    reader_response = await client.post(
        "/readers/",
        json={"name": "Artem", "email": "artem@mail.ru"},
        headers=auth_headers
    )
    reader_id = reader_response.json()["id"]

    for i in range(4):
        book_response = await client.post(
            "/books/",
            json={
                "title": f"{i}",
                "author": "Author",
                "year": 2024,
                "isbn": f"978-3-16-14841-{i}",
                "copies_available": 5
            },
            headers=auth_headers
        )

        response = await client.post(
            "/borrowing/borrow",
            json={
                "book_id": book_response.json()["id"],
                "reader_id": reader_id
            },
            headers=auth_headers
        )

        if i < 3:
            assert response.status_code == 200
        else:
            assert response.status_code == 400


async def test_return_book(client: AsyncClient, auth_headers, setup_book_and_reader):
    await client.post(
        "/borrowing/borrow",
        json={
            "book_id": setup_book_and_reader["book_id"],
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )

    response = await client.post(
        "/borrowing/return",
        json={
            "book_id": setup_book_and_reader["book_id"],
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["return_date"] is not None


async def test_return_increases_copies(client: AsyncClient, auth_headers, setup_book_and_reader):
    book_id = setup_book_and_reader["book_id"]

    await client.post(
        "/borrowing/borrow",
        json={
            "book_id": book_id,
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )

    book_borrowed = await client.get(f"/books/{book_id}")
    copies_after_borrow = book_borrowed.json()["copies_available"]

    await client.post(
        "/borrowing/return",
        json={
            "book_id": book_id,
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )

    book_returned = await client.get(f"/books/{book_id}")
    assert book_returned.json()["copies_available"] == copies_after_borrow + 1


async def test_cannot_return_not_borrowed(client: AsyncClient, auth_headers, setup_book_and_reader):
    response = await client.post(
        "/borrowing/return",
        json={
            "book_id": setup_book_and_reader["book_id"],
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )
    assert response.status_code == 400


async def test_get_reader_books(client: AsyncClient, auth_headers, setup_book_and_reader):
    await client.post(
        "/borrowing/borrow",
        json={
            "book_id": setup_book_and_reader["book_id"],
            "reader_id": setup_book_and_reader["reader_id"]
        },
        headers=auth_headers
    )

    response = await client.get(
        f"/borrowing/reader/{setup_book_and_reader['reader_id']}/books",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
