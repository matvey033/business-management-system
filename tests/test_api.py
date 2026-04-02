import pytest


@pytest.mark.asyncio
async def test_full_business_flow(ac):
    # 1. РЕГИСТРАЦИЯ И АВТОРИЗАЦИЯ

    # Регистрируем Админа
    res = await ac.post(
        "/auth/register",
        json={
            "email": "boss@mail.com",
            "password": "superpassword",
            "role": "admin",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    assert res.status_code == 201

    # Регистрируем обычного Сотрудника
    res = await ac.post(
        "/auth/register",
        json={
            "email": "worker@mail.com",
            "password": "superpassword",
            "role": "user",
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        },
    )
    assert res.status_code == 201
    worker_id = res.json()["id"]

    # Логиним Админа (получаем токен)
    res = await ac.post(
        "/auth/jwt/login",
        data={"username": "boss@mail.com", "password": "superpassword"},
    )
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Логиним Сотрудника (получаем токен)
    res = await ac.post(
        "/auth/jwt/login",
        data={"username": "worker@mail.com", "password": "superpassword"},
    )
    worker_token = res.json()["access_token"]
    worker_headers = {"Authorization": f"Bearer {worker_token}"}

    # 2. КОМАНДЫ (Создание и присоединение)

    # Админ создает команду
    res = await ac.post("/teams/", headers=admin_headers, json={"name": "Alpha Team"})
    assert res.status_code == 200
    team_code = res.json()["join_code"]

    # Админ присоединяется по коду
    await ac.post(f"/teams/join?join_code={team_code}", headers=admin_headers)

    # Сотрудник присоединяется по коду
    res = await ac.post(f"/teams/join?join_code={team_code}", headers=worker_headers)
    assert res.status_code == 200

    # 3. ЗАДАЧИ И КОММЕНТАРИИ

    # Админ ставит задачу Сотруднику
    res = await ac.post(
        "/tasks/",
        headers=admin_headers,
        json={
            "title": "Написать тесты",
            "description": "Покрыть код на 70%",
            "deadline": "2026-12-31T23:59:59",
            "assignee_id": worker_id,
        },
    )
    assert res.status_code == 200
    task_id = res.json()["id"]

    # Сотрудник пишет комментарий к задаче
    res = await ac.post(
        f"/tasks/{task_id}/comments", headers=worker_headers, json={"text": "Уже пишу!"}
    )
    assert res.status_code == 200

    # Сотрудник меняет статус задачи на "in_progress"
    res = await ac.patch(
        f"/tasks/{task_id}", headers=worker_headers, json={"status": "in_progress"}
    )

    # Сотрудник меняет статус задачи на "done" (ВЫПОЛНЕНО)
    res = await ac.patch(
        f"/tasks/{task_id}", headers=worker_headers, json={"status": "done"}
    )

    assert res.status_code == 200

    # 4. ОЦЕНКИ (Evaluation)

    # Админ (как руководитель) оценивает выполнение задачи
    res = await ac.post(
        f"/evaluations/task/{task_id}",
        headers=admin_headers,
        json={
            "score": 5,
            "comment": "Отличная работа",
            "user_id": worker_id,
        },
    )
    assert res.status_code == 200

    # 5. ВСТРЕЧИ (Meetings и защита от накладок)

    # Админ назначает себе встречу
    res = await ac.post(
        "/meetings/",
        headers=admin_headers,
        json={
            "title": "Планерка",
            "start_time": "2026-10-10T10:00:00",
            "end_time": "2026-10-10T11:00:00",
        },
    )
    assert res.status_code == 200

    # Пытаемся создать встречу, которая пересекается по времени
    res = await ac.post(
        "/meetings/",
        headers=admin_headers,
        json={
            "title": "Пересечение",
            "start_time": "2026-10-10T10:30:00",
            "end_time": "2026-10-10T11:30:00",
        },
    )
    # Ожидаем ошибку 400 (Bad Request), так как сработала наша защита!
    assert res.status_code == 400
