from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import Redis, RedisStorage

from src.config import settings

app_dir: Path = Path(__file__).parent.parent

bot = Bot(settings.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)

redis_client = Redis.from_url(settings.REDIS_URL)
storage = RedisStorage(redis_client)
dp = Dispatcher(storage=storage)
