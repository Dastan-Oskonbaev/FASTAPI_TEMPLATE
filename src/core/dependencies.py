from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-KEY")


async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Проверяет, совпадает ли переданный в заголовке X-API-Key ключ
    с секретным ключом сервера.
    """
    if api_key == settings.SECRET_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
