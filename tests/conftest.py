"""Configuration for pytest."""

import asyncio

import pytest

from src.config import settings

from .utils.alembic import alembic_config_from_url


@pytest.fixture()
def alembic_config():
    """Alembic configuration object, bound to temporary database."""
    return alembic_config_from_url(settings.DATABASE_URL)


@pytest.fixture()
def event_loop():
    """Fixture for event loop."""
    return asyncio.new_event_loop()
