import json
from datetime import datetime

import httpx

from src.config import settings


class Token:

    @classmethod
    async def get_token(cls) -> str:
        with open("data/token.json", "r") as token:
            token_file = json.load(token)

        if token_file["expires_in"] < int(datetime.now().timestamp()):
            token_file = await cls.load_new_token(token_file["refresh_token"])

        return token_file["access_token"]

    @staticmethod
    async def load_new_token(refresh_token) -> dict:
        json_data = {
            "client_id": settings.KOMMO_INTEGRATION_ID,
            "client_secret": settings.KOMMO_SECRET_KEY,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": settings.KOMMO_REDIRECT_URL,
        }

        url = f"https://{settings.KOMMO_URL_BASE}.kommo.com/oauth2/access_token"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=json_data, headers={"Content-Type": "application/json"})

        if response.status_code != 200:
            raise

        access_token_data = response.json()
        access_token_data["expires_in"] += datetime.now().timestamp()
        with open("data/token.json", "w") as token:
            json.dump(access_token_data, token)

        return access_token_data
