from pydantic import BaseModel


class BaseUser(BaseModel):
    full_name: str
    contact: str
    # rating
    # busyness
    # plane_busyness
    # card
    # speciality


class User(BaseUser):
    id: int


class BaseAdmin(BaseModel):
    full_name: str
    is_active: bool


class Admin(BaseAdmin):
    id: int
