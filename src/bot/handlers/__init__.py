from aiogram import Dispatcher
from loguru import logger

from .base import router as base_router


def setup(dp: Dispatcher):
    """Setting up miiddlewares"""
    logger.info("Settng up routers")

    dp.include_router(base_router)

    # Include your rouuters here
