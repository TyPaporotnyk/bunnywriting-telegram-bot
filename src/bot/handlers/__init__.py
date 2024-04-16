from aiogram import Dispatcher
from loguru import logger

from . import admin, author


def setup(dp: Dispatcher):
    """Setting up handlers"""
    logger.info("Setting up routers")

    admin.setup(dp)
    author.setup(dp)

    # Include your routers here
