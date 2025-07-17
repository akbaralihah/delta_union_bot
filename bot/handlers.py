from aiogram import html, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand

from bot.buttons.reply import main_menu_buttons, admin_menu_buttons
from bot.dispatcher import dp
from bot.states import UserStates
from bot.utils import track, ADMINS


@dp.message(Command(commands=["start", "restart"]))
async def command_start_handler(msg: Message) -> None:
    start_command = BotCommand(command="start", description="Start the bot")
    restart_command = BotCommand(command="restart", description="Restart the bot")
    help_command = BotCommand(command="help", description="Help")

    await msg.bot.set_my_commands(commands=[start_command, restart_command, help_command])

    answer_text = f"Assalomu alaykum😊, {html.bold(msg.from_user.full_name)}!"

    if msg.from_user.id in ADMINS:
        await msg.answer(answer_text, reply_markup=admin_menu_buttons())
    else:
        await msg.answer(answer_text, reply_markup=main_menu_buttons())


@dp.message(lambda msg: msg.text == "🔎 Yukni qidirish")
async def search_command_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer("📦 Yuk raqamini kiriting:")
    await state.set_state(UserStates.search)


@dp.message(UserStates.search)
async def cargo_number_handler(msg: Message, state: FSMContext) -> None:
    cargo_info = track(msg.text)
    await msg.reply(cargo_info)
    await state.clear()


@dp.message(F.text == "👤 Admin")
async def admin_command_handler(msg: Message) -> None:
    answer_text = "https://t.me/abdullayev1chH"
    if msg.from_user.id in ADMINS:
        await msg.answer(text=answer_text, reply_markup=admin_menu_buttons())
    await msg.answer(text=answer_text, reply_markup=main_menu_buttons())


@dp.message(Command("help"))
async def help_command_handler(msg: Message) -> None:
    pass


@dp.message(F.text == "📢 Reklama")
async def advert_command_handler(msg: Message, state: FSMContext) -> None:
    pass
