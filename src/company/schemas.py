from pydantic import BaseModel

from src.profile.schemas import ProfileSchema


class CompanySchema(BaseModel):
    id: int
    company_name: str
    owner_id: int
    profile: ProfileSchema = None

    class Config:
        from_attributes = True
