from aiogram import html, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.dispatcher import dp, bot
from bot.reply import (
    main_menu_buttons,
    admin_menu_buttons,
    choice_search_menu_buttons,
    confirm_keyboard
)
from bot.states import UserStates
from bot.utils import track, ADMINS, search_by_shipping_mark, search_by_id_in_cargo_2
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
        await state.set_state(UserStates.groupage_cargo_1)
    elif msg.text == "🚚 Cargo tracking":
        await state.set_state(UserStates.groupage_cargo_2)


@dp.message(UserStates.full_container)
async def container_number_handler(msg: Message, state: FSMContext) -> None:
    container_info = track(msg.text)
    await state.clear()
    if msg.from_user.id in ADMINS:
        await msg.reply(container_info, reply_markup=admin_menu_buttons())
    else:
        await msg.reply(container_info, reply_markup=main_menu_buttons())


@dp.message(UserStates.groupage_cargo_1)
async def cargo_number_handler(msg: Message, state: FSMContext) -> None:
    cargo_info = search_by_shipping_mark(msg.text)
    await state.clear()
    if msg.from_user.id in ADMINS:
        await msg.reply(text=cargo_info, reply_markup=admin_menu_buttons())
    else:
        await msg.reply(text=cargo_info, reply_markup=main_menu_buttons())


@dp.message(UserStates.groupage_cargo_2)
async def cargo_id_handler(msg: Message, state: FSMContext) -> None:
    cargo_info = search_by_id_in_cargo_2(msg.text)
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
async def preview_advert_handler(msg: Message, state: FSMContext) -> None:
    await state.update_data(advert_msg=msg)

    if msg.text:
        await msg.answer(text=msg.text, reply_markup=confirm_keyboard())
    elif msg.photo:
        await msg.answer_photo(photo=msg.photo[-1].file_id, caption=msg.caption or "", reply_markup=confirm_keyboard())
    elif msg.video:
        await msg.answer_video(video=msg.video.file_id, caption=msg.caption or "", reply_markup=confirm_keyboard())
    elif msg.animation:
        await msg.answer_animation(animation=msg.animation.file_id, caption=msg.caption or "",
                                   reply_markup=confirm_keyboard())
    else:
        await msg.answer("❌ Noma'lum kontent turi. Faqat matn, rasm, video yoki gif yuboring.")
        return


@dp.callback_query(F.data.in_(["confirm_send", "cancel_send"]))
async def send_advert_to_all(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    msg: Message = data.get("advert_msg")

    if callback.data == "cancel_send":
        await callback.message.edit_text("❌ Reklama yuborilishi bekor qilindi.")
        await state.clear()
        return

    user_ids = User.get_all_user_ids(session)
    success = 0
    failed = 0

    for uid in user_ids:
        try:
            if msg.text:
                await bot.send_message(uid, msg.text)
            elif msg.photo:
                await bot.send_photo(uid, msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await bot.send_video(uid, msg.video.file_id, caption=msg.caption or "")
            elif msg.animation:
                await bot.send_animation(uid, msg.animation.file_id, caption=msg.caption or "")
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
