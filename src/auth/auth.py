from fastapi_users.authentication import (
    BearerTransport,
    AuthenticationBackend,
    JWTStrategy,
)

from fastapi_users import FastAPIUsers
from src.models.user import User
from src.auth.manager import get_user_manager

from src.core.config import settings

# URL, на который пользователь будет отправлять email и пароль для получения токена
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# Настройка генерации токена (срок жизни - 1 час, то есть 3600 секунд)
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

# Переменная для проверки авторизации пользователя (используем как Depends)
current_active_user = fastapi_users.current_user(active=True)
