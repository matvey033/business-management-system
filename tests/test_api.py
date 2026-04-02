import pytest


# 1. Тест регистрации пользователя
@pytest.mark.asyncio
async def test_register(ac):
    response = await ac.post(
        "/auth/register",
        json={
            "email": "tester@example.com",
            "password": "supersecretpassword",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
            "role": "user",
        },
    )
    # Ожидаем успешное создание (201 Created)
    assert response.status_code == 201


# 2. Тест авторизации (получения токена)
@pytest.mark.asyncio
async def test_login(ac):
    response = await ac.post(
        "/auth/jwt/login",
        data={"username": "tester@example.com", "password": "supersecretpassword"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


# 3. Тест бизнес-логики: Защита от пересечения встреч
@pytest.mark.asyncio
async def test_meeting_overlap(ac):
    # Логинимся, чтобы получить токен
    login_res = await ac.post(
        "/auth/jwt/login",
        data={"username": "tester@example.com", "password": "supersecretpassword"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Создаем первую встречу (с 10:00 до 11:00)
    meet1 = await ac.post(
        "/meetings/",
        headers=headers,
        json={
            "title": "Утренняя планерка",
            "start_time": "2026-10-10T10:00:00",
            "end_time": "2026-10-10T11:00:00",
        },
    )
    assert meet1.status_code == 200

    # Пытаемся создать вторую встречу, которая накладывается (с 10:30 до 11:30)
    meet2 = await ac.post(
        "/meetings/",
        headers=headers,
        json={
            "title": "Пересекающаяся встреча",
            "start_time": "2026-10-10T10:30:00",
            "end_time": "2026-10-10T11:30:00",
        },
    )

    # Алгоритм должен заблокировать и выдать 400 Bad Request!
    assert meet2.status_code == 400
    assert "уже запланирована" in meet2.json()["detail"].lower()
