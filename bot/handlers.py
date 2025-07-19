from aiogram import html, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.reply import main_menu_buttons, admin_menu_buttons
from bot.dispatcher import dp, bot
from bot.states import UserStates
from bot.utils import track, ADMINS
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
