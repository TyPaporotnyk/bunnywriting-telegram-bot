from sqlalchemy import insert, select

from src.db.models import Admin
from src.db.repositories.abstract import Repository


class AdminRepository(Repository):
    model = Admin
