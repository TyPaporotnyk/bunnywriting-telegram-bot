from dataclasses import dataclass
from datetime import datetime
from typing import List
from urllib.parse import urlencode, urljoin

import httpx
from loguru import logger

from src.config import settings
from src.crm.exceptions import LeadNotCreated, LeadNotUpdated
from src.crm.token import Token
from src.db.schemas import LeadSchema

statuses = {
    53018507: "Нова заявка",
    53018511: "Звернувся",
    56565603: "Зведення",
    53018515: "Очікуєм",
    56600119: "Продано",
    53018519: "На модерації",
    53018603: "Знайти автора",
    53018607: "Дізнатись ціну",
    53018611: "Підтвердження автора",
    53018615: "План",
    53018619: "План готовий",
    56532691: "Правки план",
    56529915: "План відправлено",
    56532795: "План затвердженно",
    53018631: "В роботі",
    53018635: "Робота відправленна",
    56532679: "Правки",
    56532683: "Правки в роботі",
    56530895: "Правки відправленно",
    54897359: "Не відправленно",
    53018639: "Готово",
}


pipelines = {
    6132011: "Pipeline",
}


def get_lead_from_dict(data: dict) -> LeadSchema:
    lead_name = data["name"]
    lead_id = data["id"]
    custom_fields = {}
    fields = data.get("custom_fields_values", [])
    fields = fields if fields else []
    for field in fields:
        filed_id = field["field_id"]
        field_values = field["values"]
        field_type = field["field_type"]

        if field_type == "multiselect":
            field_values = [value["value"] for value in field_values]
        else:
            field_values = field["values"][0]["value"]

        custom_fields.setdefault(filed_id, field_values)

    return LeadSchema(
        id=lead_id,
        name=lead_name,
        status=statuses.get(int(data["status_id"])),
        pipeline=pipelines.get(int(data["pipeline_id"])),
        created_at=data["created_at"],
        updated_at=data["updated_at"],
        created_by=data["created_by"],
        updated_by=data["updated_by"],
        contact=custom_fields.get(254740),
        sale=custom_fields.get(1110606),
        date=custom_fields.get(254738),
        speciality=custom_fields.get(254842),
        work_type=custom_fields.get(254896),
        koef=custom_fields.get(254898, "0"),
        pages=custom_fields.get(254900),
        thema=custom_fields.get(254902),
        uniqueness=custom_fields.get(254904),
        real_deadline=custom_fields.get(254906),
        deadline_for_author=custom_fields.get(1110826),
        files=custom_fields.get(254910),
        fix_time=custom_fields.get(254964),
        author_name=custom_fields.get(254966),
        author_id=custom_fields.get(254968),
        expenses=custom_fields.get(1110830),
        expenses_status=custom_fields.get(254978),
        expenses_multy=custom_fields.get(255030),
        note=custom_fields.get(255082),
        team_lead=custom_fields.get(255084),
        priority=custom_fields.get(255096),
        sec_author=custom_fields.get(255098),
        alert=custom_fields.get(255100),
        sec_price=custom_fields.get(1110362),
        sity=custom_fields.get(255090),
        university=custom_fields.get(255092),
        faculty=custom_fields.get(255094),
        review=custom_fields.get(255088),
        costs_sum=custom_fields.get(1115269),
        correction_count=custom_fields.get(1115267),
        delivery_date=custom_fields.get(1115271),
        shtraf=custom_fields.get(1111240),
        date_done=custom_fields.get(1115271),
        plan=custom_fields.get(1112838),
        task_current=custom_fields.get(1112842),
        date_current=custom_fields.get(1112854),
        hotovo=custom_fields.get(1112846),
        redone_date=custom_fields.get(1116123),
    )


class Lead:
    @staticmethod
    def _get_api_url():
        return f"https://{settings.KOMMO_URL_BASE}.kommo.com/api/v4/leads"

    @staticmethod
    async def _get_header():
        oauth_token = await Token.get_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {oauth_token}",
        }

    @classmethod
    async def _make_update_request(cls, lead_id, json_data):
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                cls._get_api_url() + "/" + str(lead_id),
                headers=(await cls._get_header()),
                json=json_data,
            )

        if response.status_code != 200:
            logger.error(response.text)
            raise LeadNotUpdated()

        return response

    @classmethod
    async def _make_create_request(cls, json_data):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls._get_api_url(),
                headers=(await cls._get_header()),
                json=json_data,
            )

        if response.status_code != 200:
            raise LeadNotCreated()

        return response

    @classmethod
    async def create_lead(
        cls, lead_source, lead_contact, lead_work_type, lead_pages, lead_deadline, lead_theme, author_id: int
    ):
        json_data = [
            {
                "price": 0,
                "responsible_user_id": 8905311,
                "_embedded": {
                    "contacts": [
                        {
                            "id": author_id,
                        }
                    ],
                },
                "custom_fields_values": [
                    {"field_id": 254736, "values": [{"value": lead_source}]},
                    {"field_id": 254740, "values": [{"value": lead_contact}]},
                    {"field_id": 254896, "values": [{"value": lead_work_type}]},
                    {"field_id": 254900, "values": [{"value": lead_pages}]},
                    {"field_id": 254906, "values": [{"value": lead_deadline}]},
                    {"field_id": 254902, "values": [{"value": lead_theme}]},
                ],
            }
        ]

        await cls._make_create_request(json_data)

    @classmethod
    async def get_leads(cls, page: int = 0) -> List[LeadSchema]:
        params = {"limit": "250", "page": page}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        return [get_lead_from_dict(lead) for lead in response.json()["_embedded"]["leads"]]

    @classmethod
    async def get_leads_by_status(cls, status_id: int, pipeline_id: int = 6132011) -> List[LeadSchema]:
        params = {"filter[statuses][0][pipeline_id]": pipeline_id, "filter[statuses][0][status_id]": status_id}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        return [get_lead_from_dict(lead) for lead in response.json()["_embedded"]["leads"]]

    @classmethod
    async def get_lead(cls, lead_id: int) -> LeadSchema:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                cls._get_api_url() + "/" + str(lead_id),
                headers=(await cls._get_header()),
            )

        return get_lead_from_dict(response.json())

    @classmethod
    async def update_lead_status(cls, lead_id, status_id) -> bool:
        json_data = {
            "status_id": status_id,
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_author(cls, lead_id, author_crm_id, author_teamlead_id) -> bool:
        json_data = {
            "custom_fields_values": [
                {"field_id": 254968, "values": [{"value": str(author_crm_id)}]},
                # {"field_id": 1116279, "values": [{"value": str(author_crm_id)}]},
                {"field_id": 254968, "values": [{"value": str(author_crm_id)}]},
                {"field_id": 255084, "values": [{"value": str(author_teamlead_id)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_author_name(cls, lead_id, author_name) -> bool:
        json_data = {
            "custom_fields_values": [
                {"field_id": 255098, "values": [{"value": str(author_name)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_id(cls, lead_id) -> bool:
        json_data = {
            "custom_fields_values": [
                {"field_id": 254734, "values": [{"value": str(lead_id)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_price(cls, lead_id, price) -> bool:
        json_data = {
            "custom_fields_values": [
                {"field_id": 1110830, "values": [{"value": str(price)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_second_price(cls, lead_id, price):
        json_data = {
            "custom_fields_values": [
                {"field_id": 1110362, "values": [{"value": str(price)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_second_author(cls, lead_id, author_name):
        json_data = {
            "custom_fields_values": [
                {"field_id": 255098, "values": [{"value": str(author_name)}]},
            ]
        }

        await cls._make_update_request(lead_id, json_data)
