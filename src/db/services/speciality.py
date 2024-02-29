from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.specialities import SpecialityRepository


async def get_specialities(session: AsyncSession):
    speciality_repository = SpecialityRepository(session)
    specialities = await speciality_repository.get_all()
    specialities_name = [speciality.name for speciality in specialities]

    return specialities_name
