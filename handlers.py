from aiogram import html, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, BotCommand

from reply import main_menu_buttons
from utils import track


class UserStates(StatesGroup):
    main_menu = State()
    search = State()


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(msg: Message) -> None:
    start_command = BotCommand(command="start", description="Start the bot")
    restart_command = BotCommand(command="restart", description="Restart the bot")
    help_command = BotCommand(command="help", description="Help")

    await msg.bot.set_my_commands(commands=[start_command, restart_command, help_command])
    await msg.answer(f"Hello, {html.bold(msg.from_user.full_name)}!", reply_markup=main_menu_buttons())


@dp.message(lambda msg: msg.text == "🔎 Yukni qidirish")
async def search_command_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer("📦 Yuk raqamini kiriting:")
    await state.set_state(UserStates.search)


@dp.message(UserStates.search)
async def cargo_number_handler(msg: Message, state: FSMContext) -> None:
    cargo_info = track(msg.text)
    await msg.reply(cargo_info)
    await state.clear()


@dp.message(lambda msg: msg.text == "👤 Admin")
async def admin_command_handler(msg: Message) -> None:
    await msg.reply_contact("+998200158060", "Akbarali", "Salohiddinov")
