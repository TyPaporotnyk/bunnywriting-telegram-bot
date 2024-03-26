from aiogram import Dispatcher
from loguru import logger

from .admin import router as admin_router
from .author import router as author_router


def setup(dp: Dispatcher):
    """Setting up handlers"""
    logger.info("Settng up routers")

    dp.include_router(author_router)
    dp.include_router(admin_router)

    # Include your rouuters here
