from typing import List

from src.db.repositories.admin import AdminRepository


async def get_admin_ids(session) -> List[int]:
    admin_repository = AdminRepository(session)
    admin_ids = await admin_repository.get_admin_ids()

    return admin_ids


async def get_admin_authors(session, admin_id):
    admin_repository = AdminRepository(session)
    admin = await admin_repository.get(id=admin_id)

    return admin.authors


async def get_admin_author_ids(session, admin_id) -> List[int]:
    admin_repository = AdminRepository(session)
    admin = await admin_repository.get(id=admin_id)
    authors = admin.authors

    authors_ids = [author.id for author in authors]
    return authors_ids


async def get_admin_authors_payments(session, admin_id):
    ...
