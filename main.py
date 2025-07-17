import asyncio
import logging
import sys

from aiogram.types import BotCommand

from bot.dispatcher import bot
from bot.handlers import dp
from bot.utils import description_text


async def main() -> None:
    await bot.set_my_description(description=description_text)
    start_command = BotCommand(command="start", description="Start the bot")
    restart_command = BotCommand(command="restart", description="Restart the bot")
    help_command = BotCommand(command="help", description="Help")

    await bot.set_my_commands(commands=[start_command, restart_command, help_command])
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
