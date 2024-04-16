from aiogram import Dispatcher
from loguru import logger

from .base import router as base_router
from .create_author import router as create_author_router
from .mailing import router as mailing_router
from .urgent_list import router as urgent_list_router


def setup(dp: Dispatcher):
    """Setting up admin routers"""
    logger.info("Setting up admin routers")

    dp.include_router(base_router)
    dp.include_router(create_author_router)
    dp.include_router(mailing_router)
    dp.include_router(urgent_list_router)
