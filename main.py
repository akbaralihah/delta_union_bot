import asyncio
import logging
import sys

from aiogram.types import BotCommand

from bot.dispatcher import bot, dp
from bot.translations import description_text
from db.configs import engine, Base

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def on_startup() -> None:
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Set bot commands
    await bot.set_my_description(description=description_text["UZ"])
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="restart", description="Restart the bot"),
        BotCommand(command="help", description="Help")
    ]
    await bot.set_my_commands(commands=commands)
    logger.info("Bot started successfully")


async def main() -> None:
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
