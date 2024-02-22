from typing import List

from src.db.repositories.admin import AdminRepository


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
