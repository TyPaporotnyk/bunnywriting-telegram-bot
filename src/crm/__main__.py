import sys

import requests

from src.config import settings


def get_toket(code: str):
    json_data = {
        "client_id": settings.KOMMO_INTEGRATION_ID,
        "client_secret": settings.KOMMO_SECRET_KEY,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.KOMMO_REDIRECT_URL,
    }
    response = requests.post(
        "https://bunnywriting777.kommo.com/oauth2/access_token",
        headers={"Content-Type": "application/json"},
        json=json_data,
    )
    print(response.text)


if __name__ == "__main__":
    get_toket(sys.argv[1])
