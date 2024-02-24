import json

from aiogram import F, Router, types

from src.crm.author import Author
from src.crm.lead import Lead

router = Router(name="base")


@router.message(F.text == "Тест")
async def test(message: types.Message, session):
    authors = await Lead.get_lead(15738967)

    with open("lead_data.json", "w") as file:
        json.dump(authors, file, indent=4, ensure_ascii=False)
