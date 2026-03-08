from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from bot.routers import admin, cargo, common
from bot.middlewares.db import DbSessionMiddleware
from db.configs import AsyncSessionLocal, redis_client
from settings import settings


bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=RedisStorage(redis=redis_client))

# Register Middleware
dp.update.middleware(DbSessionMiddleware(session_pool=AsyncSessionLocal))

# Register Routers
dp.include_router(common.router)
dp.include_router(cargo.router)
dp.include_router(admin.router)
