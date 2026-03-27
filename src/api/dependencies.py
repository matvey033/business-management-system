from fastapi import Depends, HTTPException
from src.models.user import User, Role
from src.auth.auth import current_active_user


# Проверка: Только Администратор
async def get_current_admin(user: User = Depends(current_active_user)):
    if user.role != Role.admin:
        raise HTTPException(
            status_code=403, detail="Только администратор может выполнять это действие"
        )
    return user


# Проверка: Руководитель (Менеджер или Администратор)
async def get_manager_user(user: User = Depends(current_active_user)):
    if user.role not in [Role.manager, Role.admin]:
        raise HTTPException(
            status_code=403, detail="Только руководитель может выполнять это действие"
        )
    return user
