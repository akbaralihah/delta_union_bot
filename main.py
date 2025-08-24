import asyncio
import logging
import sys

from aiogram.types import BotCommand

from bot.dispatcher import bot
from bot.handlers import dp
from bot.translations import description_text

log_format = "%(asctime)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# logger configuration
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt=date_format,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def main() -> None:
    await bot.set_my_description(description=description_text["UZ"])
    start_command = BotCommand(command="start", description="Start the bot")
    restart_command = BotCommand(command="restart", description="Restart the bot")
    help_command = BotCommand(command="help", description="Help")

    await bot.set_my_commands(commands=[start_command, restart_command, help_command])
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
