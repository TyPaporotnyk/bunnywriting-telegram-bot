from dataclasses import dataclass
from urllib.parse import urlencode, urljoin

import httpx
from loguru import logger

from src.config import settings
from src.crm.exceptions import LeadNotCreated, LeadNotUpdated
from src.crm.token import Token


@dataclass
class LeadFieds:
    TELEGRAM_ID = 1110792
    CARD_NUMBER = 1111072
    IS_AUCTION = 1111074
    TELEGRAM_USERNAME = 1111076
    AUTHOR_ID = 1111078
    POSITION = 254484
    TEAMLEAD_ID = 1110804
    RATING = 1110796
    PLANE_BUSINESS = 1110798
    BUSINESSS = 1110800
    OPEN_LEADS = 1110794
    COMMENT = 1110806
    SPECIALITIES = 1110802
    IS_AUTHOR = 1110790
    TERM_OF_USE = 1114546


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
            response = await client.post(
                cls._get_api_url() + "/" + str(lead_id),
                headers=(await cls._get_header()),
                json=json_data,
            )

        if response.status_code != 200:
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
    async def get_leads(cls, page):
        params = {"limit": "250", "page": page}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        return response.json()["_embedded"]["leads"]

    @classmethod
    async def get_leads_by_status(cls, status_id: int, pipeline_id: int = 6132011):
        params = {"filter[statuses][0][pipeline_id]": pipeline_id, "filter[statuses][0][status_id]": status_id}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        return response.json()

    @classmethod
    async def get_lead(cls, lead_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                cls._get_api_url() + "/" + str(lead_id),
                headers=(await cls._get_header()),
            )

        return response.json()

    @classmethod
    async def update_lead_status(cls, lead_id, status_id) -> bool:
        json_data = {
            "status_id": status_id,
        }

        await cls._make_update_request(lead_id, json_data)

    @classmethod
    async def update_lead_author(cls, lead_id, author_crm_id, uthor_teamlead_id) -> bool:
        json_data = {
            "custom_fields_values": [
                {"field_id": 254968, "values": [{"value": str(author_crm_id)}]},
                {"field_id": 1116279, "values": [{"value": str(author_crm_id)}]},
                {"field_id": 255084, "values": [{"value": str(uthor_teamlead_id)}]},
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
