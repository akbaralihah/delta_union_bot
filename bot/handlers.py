from aiogram import html, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.dispatcher import dp, bot
from bot.reply import main_menu_buttons, admin_menu_buttons, choice_search_menu_buttons
from bot.states import UserStates
from bot.utils import track, ADMINS, search_by_shipping_mark
from db.configs import session
from db.models import User


@dp.message(Command(commands=["start", "restart"]))
async def command_start_handler(msg: Message) -> None:
    answer_text = f"Assalomu alaykum😊, {html.bold(msg.from_user.full_name)}!"
    User.upsert(
        session=session,
        user_id=msg.from_user.id,
        full_name=msg.from_user.full_name,
        username=msg.from_user.username
    )
    if msg.from_user.id in ADMINS:
        await msg.answer(answer_text, reply_markup=admin_menu_buttons())
    else:
        await msg.answer(answer_text, reply_markup=main_menu_buttons())


@dp.message(F.text == "🔎 Yukni qidirish")
async def search_command_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer(text="Qidiruv uchun bo'limni tanlang👇", reply_markup=choice_search_menu_buttons())
    await state.set_state(UserStates.search_choice_menu)


@dp.message(UserStates.search_choice_menu)
async def search_choice_cmd_handler(msg: Message, state: FSMContext) -> None:
    await msg.answer("📦 Yuk raqamini kiriting:")
    if msg.text == "📦 Shaxsiy konteyner":
        await state.set_state(UserStates.full_container)
    elif msg.text == "🧩 Yig'ma konteyner":
        await state.set_state(UserStates.groupage_cargo)


@dp.message(UserStates.full_container)
async def container_number_handler(msg: Message, state: FSMContext) -> None:
    container_info = track(msg.text)
    await state.clear()
    if msg.from_user.id in ADMINS:
        await msg.reply(container_info, reply_markup=admin_menu_buttons())
    else:
        await msg.reply(container_info, reply_markup=main_menu_buttons())


@dp.message(UserStates.groupage_cargo)
async def cargo_number_handler(msg: Message, state: FSMContext) -> None:
    cargo_info = search_by_shipping_mark(msg.text)
    await state.clear()
    if msg.from_user.id in ADMINS:
        await msg.reply(text=cargo_info, reply_markup=admin_menu_buttons())
    else:
        await msg.reply(text=cargo_info, reply_markup=main_menu_buttons())


@dp.message(F.text == "👤 Admin")
async def admin_command_handler(msg: Message) -> None:
    answer_text = "https://t.me/Mr_bob0921"
    if msg.from_user.id in ADMINS:
        await msg.answer(text=answer_text, reply_markup=admin_menu_buttons())
    await msg.answer(text=answer_text, reply_markup=main_menu_buttons())


@dp.message(Command("help"))
async def help_command_handler(msg: Message) -> None:
    pass


@dp.message(F.text == "📢 Reklama")
async def advert_command_handler(msg: Message, state: FSMContext) -> Message | None:
    if msg.from_user.id not in ADMINS:
        return await msg.answer(text="❌ Sizda bu amalni bajarishga ruxsat yo'q.")

    await msg.answer(text="📨 Reklama matnini yuboring (matn, rasm, video yoki gif bo‘lishi mumkin):")
    await state.set_state(UserStates.advert)
    return None


@dp.message(UserStates.advert)
async def send_advert_to_all(msg: Message, state: FSMContext):
    user_ids = User.get_all_user_ids(session)
    success = 0
    failed = 0

    for uid in user_ids:
        try:
            if msg.text:
                await bot.send_message(uid, msg.text)
            elif msg.photo:
                await bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption)
            elif msg.video:
                await bot.send_video(uid, msg.video.file_id, caption=msg.caption)
            elif msg.animation:
                await bot.send_animation(uid, msg.animation.file_id, caption=msg.caption)
            else:
                continue
            success += 1
        except TelegramBadRequest:
            failed += 1
            continue
        except Exception as e:
            print(f"Xatolik: {e}")
            failed += 1
            continue

    await msg.answer(f"✅ Reklama yuborildi.\n📨 Qabul qilinganlar: {success}\n❌ Xatoliklar: {failed}")
    await state.clear()
