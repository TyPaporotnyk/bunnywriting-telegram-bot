from dataclasses import dataclass
from urllib.parse import urlencode, urljoin

import httpx

from src.config import settings
from src.crm.exceptions import AuthorNotCreated, AuthorNotUpdated
from src.crm.token import Token


@dataclass
class AuthorFieds:
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
            response = await client.post(
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

        return response.json()

    @classmethod
    async def get_authors(cls, page):
        """Получает все аторов"""
        params = {"query": "True", "limit": "250", "page": page}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                urljoin(cls._get_api_url(), "?" + urlencode(params)),
                headers=(await cls._get_header()),
            )

        if response.status_code != 200:
            raise AuthorNotCreated()

        return response.json()

    @classmethod
    async def create_author(cls, telegram_id, user_id, full_name, raiting, team_lead) -> bool:
        """Создает нового автора"""
        first_name, last_name = full_name.split(" ")
        json_data = [
            {
                "first_name": first_name,
                "last_name": last_name,
                "custom_fields_values": [
                    {"field_id": AuthorFieds.TELEGRAM_ID, "values": [{"value": str(telegram_id)}]},
                    {"field_id": AuthorFieds.RATING, "values": [{"value": raiting}]},
                    {"field_id": AuthorFieds.AUTHOR_ID, "values": [{"value": str(user_id)}]},
                    {"field_id": AuthorFieds.TEAMLEAD_ID, "values": [{"value": str(team_lead)}]},
                    {"field_id": AuthorFieds.PLANE_BUSINESS, "values": [{"value": 0}]},
                    {"field_id": AuthorFieds.BUSINESSS, "values": [{"value": 0}]},
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
                {"field_id": AuthorFieds.TELEGRAM_USERNAME, "values": [{"value": username}]},
            ]
        }

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_plane_business(cls, author_id, business):
        """Обновляет плановую нагруженность автора"""
        json_data = {"custom_fields_values": [{"field_id": 1110798, "values": [{"value": business}]}]}

        await cls._make_update_request(author_id, json_data)

    @classmethod
    async def update_author_busyness(cls, author_id, bussines: float, open_leads: int):
        """Обновляет нагруженность автора"""
        json_data = {
            "custom_fields_values": [
                {
                    "field_id": AuthorFieds.BUSINESSS,
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
