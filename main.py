import asyncio
import logging
import sys

from bot.dispatcher import bot
from bot.handlers import dp
from bot.utils import description_text


async def main() -> None:
    await bot.set_my_description(description=description_text)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
