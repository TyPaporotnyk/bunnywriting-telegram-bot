from aiogram import Dispatcher
from loguru import logger

from .base import router as base_router


def setup(dp: Dispatcher):
    """Setting up admin routers"""
    logger.info("Setting up author routers")

    dp.include_router(base_router)
