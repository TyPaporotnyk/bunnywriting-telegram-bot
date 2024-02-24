from typing import List

from src.db.models import Lead
from src.db.repositories.admin import AdminRepository
from src.db.services.user import get_author_leads


async def get_admin_ids(session) -> List[int]:
    admin_repository = AdminRepository(session)
    admins = await admin_repository.get_all()
    admin_ids = [admin.id for admin in admins]

    return admin_ids


async def get_admin_author_ids(session, admin_id) -> List[int]:
    admin_repository = AdminRepository(session)

    admin = await admin_repository.get(id=admin_id)
    authors_ids = [author.id for author in admin.authors]

    return authors_ids


async def get_admin_author_leads(session, admin_id) -> List[Lead]:
    authors_ids = await get_admin_author_ids(session, admin_id)
    authors_leads = [await get_author_leads(session, author_id) for author_id in authors_ids]

    return authors_leads


async def get_admin_author_payments(session, admin_id):
    authors_leads = await get_admin_author_leads(session, admin_id)

    print(authors_leads)


async def get_admin_author_deadlines(session, admin_id):
    authors_leads = await get_admin_author_leads(session, admin_id)

    print(authors_leads)
