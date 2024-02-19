from aiogram import Dispatcher
from loguru import logger

from src.db import session_maker

from .database import DatabaseMiddleware


def setup(dp: Dispatcher):
    """Setting up miiddlewares"""
    logger.info("Setting up middlewares")

    dp.update.middleware(DatabaseMiddleware(session_pool=session_maker))

    # Include your middlewaares here
