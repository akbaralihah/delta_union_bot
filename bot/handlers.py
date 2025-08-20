from aiogram import html, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.dispatcher import dp, bot
from bot.reply import (
    main_menu_buttons,
    admin_menu_buttons,
    choice_search_menu_buttons,
    confirm_keyboard, language_keyboard
)
from bot.states import UserStates
from bot.translations import translate
from bot.utils import track, ADMINS, search_by_shipping_mark, search_cargo
from db.configs import session
from db.models import User


@dp.message(Command(commands=["start", "restart"]))
async def command_start_handler(msg: Message) -> None:
    user = User.get_by_user_id(msg.from_user.id, session=session)

    if not user:
        User.upsert(
            session=session,
            user_id=msg.from_user.id,
            full_name=msg.from_user.full_name,
            username=msg.from_user.username
        )
        await msg.answer(
            translate("UZ", "choose_language"),
            reply_markup=language_keyboard("UZ")
        )
        return

    if not user.lang:
        await msg.answer(
            translate("UZ", "choose_language"),
            reply_markup=language_keyboard("UZ")
        )
        return

    lang = user.lang
    answer_text = translate(lang, "greeting", name=html.bold(msg.from_user.full_name))

    if msg.from_user.id in ADMINS:
        await msg.answer(answer_text, reply_markup=admin_menu_buttons(lang))
    else:
        await msg.answer(answer_text, reply_markup=main_menu_buttons(lang))


@dp.message(F.text == translate("UZ", "change_language"))
@dp.message(F.text == translate("RU", "change_language"))
async def change_language(msg: Message):
    lang = User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(
        translate(lang, "choose_language"),
        reply_markup=language_keyboard(lang)
    )


@dp.callback_query(F.data.startswith("set_lang_"))
async def set_language(call: CallbackQuery):
    lang = call.data.split("_")[-1]
    User.update_user_lang(call.from_user.id, lang, session=session)
    await call.message.edit_text(translate(lang, "lang_updated"))
    if call.from_user.id in ADMINS:
        await call.message.answer(
            translate(lang, "main_menu"),
            reply_markup=admin_menu_buttons(lang)
        )
    else:
        await call.message.answer(
            translate(lang, "main_menu"),
            reply_markup=main_menu_buttons(lang)
        )

    await call.answer()


@dp.message(F.text == translate("UZ", "search_cargo"))
@dp.message(F.text == translate("RU", "search_cargo"))
async def search_command_handler(msg: Message, state: FSMContext) -> None:
    lang = User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(
        text=translate(lang, "choose_search"),
        reply_markup=choice_search_menu_buttons(lang)
    )
    await state.set_state(UserStates.search_choice_menu)


@dp.message(UserStates.search_choice_menu)
async def search_choice_cmd_handler(msg: Message, state: FSMContext) -> None:
    lang = User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(translate(lang, "enter_cargo_number"))
    if msg.text == translate(lang, "full_container"):
        await state.set_state(UserStates.full_container)
    elif msg.text == translate(lang, "groupage_cargo"):
        await state.set_state(UserStates.groupage_cargo_1)
    elif msg.text == translate(lang, "cargo_tracking"):
        await state.set_state(UserStates.groupage_cargo_2)


@dp.message(UserStates.full_container)
async def container_number_handler(msg: Message, state: FSMContext) -> None:
    user = msg.from_user
    lang = User.get_user_lang(user.id, session=session)
    response: dict = track(msg.text, lang)
    message_text = response.get("message")
    await state.clear()
    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ *Error:* `{response['message']}`\n" \
                 f"👤 *From:* [{user.full_name}](tg://user?id={user.id})",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    if msg.from_user.id in ADMINS:
        await msg.reply(
            text=message_text,
            reply_markup=admin_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await msg.reply(
            text=message_text,
            reply_markup=main_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )


@dp.message(UserStates.groupage_cargo_1)
async def cargo_number_handler(msg: Message, state: FSMContext) -> None:
    user = User.get_by_user_id(msg.from_user.id, session)
    lang = User.get_user_lang(user.user_id, session)
    response = search_by_shipping_mark(msg.text, lang)
    message_text = response["message"]
    await state.clear()
    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ *Error:* `{response['message']}`\n" \
                 f"👤 *From:* [{user.full_name}](tg://user?id={user.id})",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    if msg.from_user.id in ADMINS:
        await msg.reply(
            text=message_text,
            reply_markup=admin_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await msg.reply(
            text=message_text,
            reply_markup=main_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )


@dp.message(UserStates.groupage_cargo_2)
async def cargo_id_handler(msg: Message, state: FSMContext) -> None:
    user = User.get_by_user_id(msg.from_user.id, session)
    lang = User.get_user_lang(user.id, session)
    response = search_cargo(msg.text, lang)
    message_text = response["message"]
    await state.clear()
    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ *Error:* `{response['message']}`\n" \
                 f"👤 *From:* [{user.full_name}](tg://user?id={user.id})",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    if msg.from_user.id in ADMINS:
        await msg.reply(
            text=message_text,
            reply_markup=admin_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await msg.reply(
            text=message_text,
            reply_markup=main_menu_buttons(lang),
            parse_mode=ParseMode.MARKDOWN
        )


@dp.message(F.text == translate("UZ", "admin"))
@dp.message(F.text == translate("RU", "admin"))
async def admin_command_handler(msg: Message) -> None:
    lang = User.get_user_lang(msg.from_user.id, session)
    answer_text = "https://t.me/Mr_bob0921"
    if msg.from_user.id in ADMINS:
        await msg.answer(
            text=answer_text,
            reply_markup=admin_menu_buttons(lang)
        )
    await msg.answer(
        text=answer_text,
        reply_markup=main_menu_buttons(lang)
    )


@dp.message(Command("help"))
async def help_command_handler(msg: Message) -> None:
    pass


@dp.message(F.text == translate("UZ", "advert"))
@dp.message(F.text == translate("RU", "advert"))
async def advert_command_handler(msg: Message, state: FSMContext) -> Message | None:
    lang = User.get_user_lang(msg.from_user.id, session)
    if msg.from_user.id not in ADMINS:
        return await msg.answer(translate(lang, "no_permission"))
    await msg.answer(translate(lang, "send_advert"))
    await state.set_state(UserStates.advert)
    return None


@dp.message(UserStates.advert)
async def preview_advert_handler(msg: Message, state: FSMContext) -> None:
    lang = User.get_user_lang(msg.from_user.id, session)
    await state.update_data(advert_msg=msg)

    if msg.text:
        await msg.answer(
            text=msg.text,
            reply_markup=confirm_keyboard(lang)
        )
    elif msg.photo:
        await msg.answer_photo(
            photo=msg.photo[-1].file_id,
            caption=msg.caption or "",
            reply_markup=confirm_keyboard(lang))
    elif msg.video:
        await msg.answer_video(
            video=msg.video.file_id,
            caption=msg.caption or "",
            reply_markup=confirm_keyboard(lang)
        )
    elif msg.animation:
        await msg.answer_animation(
            animation=msg.animation.file_id,
            caption=msg.caption or "",
            reply_markup=confirm_keyboard(lang)
        )
    else:
        await msg.answer(translate(lang, "unknown_content"))
        return


@dp.callback_query(F.data.in_(["confirm_send", "cancel_send"]))
async def send_advert_to_all(callback: CallbackQuery, state: FSMContext) -> None:
    lang = User.get_user_lang(callback.from_user.id, session)
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    data = await state.get_data()
    msg: Message = data.get("advert_msg")

    if callback.data == "cancel_send":
        await callback.message.answer(translate(lang, "advert_cancelled"))
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
            print(f"Error: {e}")
            failed += 1
            continue

    await callback.message.answer(
        translate(lang, "advert_sent", success=success, failed=failed)
    )
    await state.clear()
