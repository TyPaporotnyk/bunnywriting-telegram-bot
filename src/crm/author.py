from dataclasses import dataclass
from typing import List
from urllib.parse import urlencode, urljoin

import httpx
from loguru import logger

from src.config import settings
from src.crm.exceptions import AuthorNotCreated, AuthorNotUpdated
from src.crm.token import Token
from src.db.schemas import AuthorSchema, SpecialitySchema


@dataclass
class AuthorFieds:
    TELEGRAM_ID = 1110792
    CARD_NUMBER = 1111072
    IS_AUCTION = 1111074
    TELEGRAM_URL = 1111076
    CUSTOM_ID = 1111078
    POSITION = 254484
    TEAMLEAD_ID = 1110804
    RATING = 1110796
    PLANE_BUSYNESS = 1110798
    BUSYNESS = 1110800
    OPEN_LEADS = 1110794
    COMMENT = 1110806
    SPECIALITIES = 1110802
    IS_AUTHOR = 1110790
    TERM_OF_USE = 1114546


def get_author_from_dict(data: dict):
    name = data["name"]
    author_id = data["id"]
    custom_fields = {}
    fields = data.get("custom_fields_values", [])

    for field in fields:
        filed_id = field["field_id"]
        field_values = field["values"]
        field_type = field["field_type"]

        if field_type == "multiselect":
            field_values = [value["value"] for value in field_values]
        else:
            field_values = field["values"][0]["value"]

        custom_fields.setdefault(filed_id, field_values)

    return AuthorSchema(
        name=name,
        id=author_id,
        telegram_id=custom_fields.get(AuthorFieds.TELEGRAM_ID),
        custom_id=custom_fields.get(AuthorFieds.CUSTOM_ID),
        rating=custom_fields.get(AuthorFieds.RATING),
        admin_id=custom_fields.get(AuthorFieds.TEAMLEAD_ID),
        plane_busyness=custom_fields.get(AuthorFieds.PLANE_BUSYNESS),
        busyness=custom_fields.get(AuthorFieds.BUSYNESS),
        open_leads=custom_fields.get(AuthorFieds.OPEN_LEADS),
        auction=custom_fields.get(AuthorFieds.IS_AUCTION),
        card_number=custom_fields.get(AuthorFieds.CARD_NUMBER),
        telegram_url=custom_fields.get(AuthorFieds.TELEGRAM_URL),
        specialities=[
            SpecialitySchema(name=speciality) for speciality in custom_fields.get(AuthorFieds.SPECIALITIES, [])
        ],
    )


class Author:
    @staticmethod
    def _get_api_url():
        return f"https://{settings.KOMMO_URL_BASE}.kommo.com/api/v4/contacts"

    @staticmethod
    async def _get_header():
        oauth_token = await Token.get_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {oauth_token}",
        }

    @classmethod
    async def _make_update_request(cls, author_id, json_data):
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                cls._get_api_url() + "/" + str(author_id),
                headers=(await cls._get_header()),
                json=json_data,
            )

        if response.status_code != 200:
            raise AuthorNotUpdated()

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
            raise AuthorNotCreated()

        return response

    @classmethod
    async def get_author(cls, author_id):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                cls._get_api_url() + "/" + str(author_id),
                headers=(await cls._get_header()),
            )

        return get_author_from_dict(response.json())

    @classmethod
    async def get_authors(cls, page: int = 0) -> List[AuthorSchema]:
        """Получает все аторов"""
        params = {"query": "True", "limit": "250", "page": page}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        if response.status_code != 200:
            raise AuthorNotCreated()

        return [get_author_from_dict(author) for author in response.json()["_embedded"]["contacts"]]

    @classmethod
    async def create_author(cls, telegram_id, user_id, full_name, rating, team_lead) -> bool:
        """Создает нового автора"""
        first_name, last_name = full_name.split(" ")
        json_data = [
            {
                "first_name": first_name,
                "last_name": last_name,
                "custom_fields_values": [
                    {"field_id": AuthorFieds.TELEGRAM_ID, "values": [{"value": str(telegram_id)}]},
                    {"field_id": AuthorFieds.RATING, "values": [{"value": rating}]},
                    {"field_id": AuthorFieds.CUSTOM_ID, "values": [{"value": str(user_id)}]},
                    {"field_id": AuthorFieds.TEAMLEAD_ID, "values": [{"value": str(team_lead)}]},
                    {"field_id": AuthorFieds.PLANE_BUSYNESS, "values": [{"value": 0}]},
                    {"field_id": AuthorFieds.BUSYNESS, "values": [{"value": 0}]},
                    {"field_id": AuthorFieds.OPEN_LEADS, "values": [{"value": 0}]},
                    {"field_id": AuthorFieds.IS_AUTHOR, "values": [{"value": "True"}]},
                    {"field_id": AuthorFieds.IS_AUCTION, "values": [{"value": "True"}]},
                ],
            },
        ]

        await cls._make_create_request(json_data)

    @classmethod
    async def register_author(cls, author_id, card_number, specialities, username):
        """Регистрирует нового автора"""
        json_data = {
            "custom_fields_values": [
                {
                    "field_id": AuthorFieds.SPECIALITIES,
                    "values": [{"value": speciality} for speciality in specialities],
                },
                {"field_id": AuthorFieds.CARD_NUMBER, "values": [{"value": card_number}]},
                {"field_id": AuthorFieds.TELEGRAM_URL, "values": [{"value": username}]},
            ]
        }

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_plane_busyness(cls, author_id, busyness):
        """Обновляет плановую нагруженность автора"""
        json_data = {
            "custom_fields_values": [{"field_id": AuthorFieds.PLANE_BUSYNESS, "values": [{"value": busyness}]}]
        }

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_author_busyness_and_open_leads(cls, author_id, bussines: float, open_leads: int):
        """Обновляет нагруженность автора"""
        json_data = {
            "custom_fields_values": [
                {
                    "field_id": AuthorFieds.BUSYNESS,
                    "values": [{"value": float(bussines) if bussines is not None else 0}],
                },
                {"field_id": AuthorFieds.OPEN_LEADS, "values": [{"value": int(open_leads)}]},
            ]
        }

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_author_specialities(cls, author_id, specialities) -> bool:
        """Обновляет специальности автора"""
        json_data = {
            "custom_fields_values": [
                {
                    "field_id": AuthorFieds.SPECIALITIES,
                    "values": [{"value": speciality} for speciality in specialities],
                },
            ]
        }

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_author_auction(cls, author_id, is_active: bool):
        """Обновляет возможность автора учавствовать в аукционе"""
        json_data = {
            "custom_fields_values": [
                {"field_id": AuthorFieds.IS_AUCTION, "values": [{"value": str(is_active)}]},
            ]
        }

        await cls._make_update_request(author_id, json_data)
