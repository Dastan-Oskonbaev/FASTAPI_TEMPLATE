from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import BaseRepository
from src.profile.models import Profile


class AuthService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Profile, session)

    async def get_by_login(self, login: str):
        stmt = select(self.model).where(self.model.login == login)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
