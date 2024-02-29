from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SpecialitySchema(BaseModel):
    name: str


class AuthorSchema(BaseModel):
    id: int
    telegram_id: Optional[int]
    custom_id: Optional[int]
    name: Optional[str]
    raiting: Optional[int]
    admin_id: Optional[int]
    plane_bussyness: Optional[int]
    bussynes: Optional[float]
    open_leads: Optional[int]
    auction: Optional[bool]
    card_number: Optional[str]
    telegram_url: Optional[str]
    specialities: List[SpecialitySchema]

    def __hash__(self) -> int:
        return self.id


class LeadSchema(BaseModel):
    id: int
    pipeline: str
    status: Optional[str]
    name: str
    created_at: datetime
    updated_at: datetime
    created_by: datetime
    updated_by: datetime
    contact: Optional[str]
    sale: Optional[int]
    date: Optional[datetime]
    speciality: Optional[str]
    work_type: Optional[str]
    koef: Optional[float]
    pages: Optional[str]
    thema: Optional[str]
    uniqueness: Optional[str]
    real_deadline: Optional[str]
    deadline_for_author: Optional[datetime]
    files: Optional[str]
    fix_time: Optional[int]
    author_name: Optional[str]
    author_id: Optional[str]
    expenses: Optional[int]
    expenses_status: Optional[int]
    expenses_multy: Optional[int]
    note: Optional[str]
    team_lead: Optional[int]
    priority: Optional[int]
    sec_author: Optional[str]
    alert: Optional[int]
    sec_price: Optional[int]
    sity: Optional[int]
    university: Optional[str]
    faculty: Optional[int]
    review: Optional[str]
    costs_sum: Optional[int]
    correction_count: Optional[int]
    delivery_date: Optional[int]
    shtraf: Optional[int]
    date_done: Optional[int]
    plan: Optional[str]
    task_current: Optional[str]
    date_current: Optional[int]
    hotovo: Optional[str]
    redone_date: Optional[int]

    def __hash__(self) -> int:
        return self.id
