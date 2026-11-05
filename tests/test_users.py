def test_create_and_get_user(client) -> None:
    create_response = client.post(
        "/users",
        json={"name": "Ada Lovelace", "email": "ada@example.com"},
    )

    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": user_id,
        "name": "Ada Lovelace",
        "email": "ada@example.com",
    }


def test_get_missing_user(client) -> None:
    response = client.get("/users/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_duplicate_email_returns_conflict(client) -> None:
    payload = {"name": "Grace Hopper", "email": "grace@example.com"}

    first_response = client.post("/users", json=payload)
    second_response = client.post(
        "/users",
        json={"name": "Another Grace", "email": payload["email"]},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "A user with this email already exists"
    }


def test_invalid_email_returns_validation_error(client) -> None:
    response = client.post(
        "/users",
        json={"name": "Invalid Email", "email": "not-an-email"},
    )

    assert response.status_code == 422


def test_list_users_returns_users_in_id_order(client) -> None:
    client.post(
        "/users",
        json={"name": "First User", "email": "first@example.com"},
    )
    client.post(
        "/users",
        json={"name": "Second User", "email": "second@example.com"},
    )

    response = client.get("/users")

    assert response.status_code == 200
    assert [user["name"] for user in response.json()] == ["First User", "Second User"]


def test_list_users_supports_pagination(client) -> None:
    for index in range(1, 4):
        client.post(
            "/users",
            json={
                "name": f"User {index}",
                "email": f"user{index}@example.com",
            },
        )

    first_page = client.get("/users", params={"skip": 0, "limit": 2})
    second_page = client.get("/users", params={"skip": 2, "limit": 2})

    assert first_page.status_code == 200
    assert [user["name"] for user in first_page.json()] == ["User 1", "User 2"]
    assert second_page.status_code == 200
    assert [user["name"] for user in second_page.json()] == ["User 3"]


def test_list_users_combines_name_filter_and_pagination(client) -> None:
    for name, email in [
        ("Ada Lovelace", "ada@example.com"),
        ("Grace Hopper", "grace@example.com"),
        ("Ada Byron", "byron@example.com"),
    ]:
        client.post("/users", json={"name": name, "email": email})

    response = client.get("/users", params={"name": "Ada", "skip": 1, "limit": 1})

    assert response.status_code == 200
    assert [user["name"] for user in response.json()] == ["Ada Byron"]


def test_list_users_rejects_invalid_pagination_parameters(client) -> None:
    negative_skip = client.get("/users", params={"skip": -1})
    zero_limit = client.get("/users", params={"limit": 0})
    excessive_limit = client.get("/users", params={"limit": 101})

    assert negative_skip.status_code == 422
    assert zero_limit.status_code == 422
    assert excessive_limit.status_code == 422
