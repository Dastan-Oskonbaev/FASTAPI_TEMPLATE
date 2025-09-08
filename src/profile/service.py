from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import BaseRepository
from src.profile.models import Profile


class ProfileService(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(Profile, session)
