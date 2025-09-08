from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.profile.models import Profile


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String, primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("profile.id"), nullable=False)

    profile = relationship("Profile", back_populates="company")


Profile.posts = relationship("Company",  back_populates="profile")
