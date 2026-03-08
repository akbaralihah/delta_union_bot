import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)

from bot.reply import (
    main_menu_buttons,
    admin_menu_buttons,
    confirm_keyboard
)
from bot.states import UserStates
from bot.translations import translate
from db.models import User
from settings import settings

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text.in_([translate("UZ", "admin"), translate("RU", "admin")]))
async def admin_command_handler(msg: Message, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    answer_text = "https://t.me/Mr_bob0921"
    
    if msg.from_user.id in settings.ADMINS:
        await msg.answer(text=answer_text, reply_markup=admin_menu_buttons(lang))
    else:
        await msg.answer(text=answer_text, reply_markup=main_menu_buttons(lang))


@router.message(F.text.in_([translate("UZ", "advert"), translate("RU", "advert")]))
async def advert_command_handler(msg: Message, state: FSMContext, session: AsyncSession) -> Message | None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    
    if msg.from_user.id not in settings.ADMINS:
        return await msg.answer(translate(lang, "no_permission"))
    
    await msg.answer(translate(lang, "send_advert"))
    await state.set_state(UserStates.advert)
    return None


@router.message(UserStates.advert)
async def preview_advert_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await state.update_data(advert_msg_id=msg.message_id, advert_chat_id=msg.chat.id)

    reply_markup = confirm_keyboard(lang)
    if msg.text:
        await msg.answer(msg.text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif msg.photo:
        await msg.answer_photo(msg.photo[-1].file_id, caption=msg.caption, reply_markup=reply_markup)
    elif msg.video:
        await msg.answer_video(msg.video.file_id, caption=msg.caption, reply_markup=reply_markup)
    elif msg.animation:
        await msg.answer_animation(msg.animation.file_id, caption=msg.caption, reply_markup=reply_markup)
    else:
        await msg.answer(translate(lang, "unknown_content"))


@router.callback_query(F.data.in_(["confirm_send", "cancel_send"]))
async def send_advert_to_all(callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    lang = await User.get_user_lang(callback.from_user.id, session=session)
    
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass

    if callback.data == "cancel_send":
        await callback.message.answer(translate(lang, "advert_cancelled"))
        await state.clear()
        return

    data = await state.get_data()
    msg_id = data.get("advert_msg_id")
    chat_id = data.get("advert_chat_id")

    user_ids = await User.get_all_user_ids(session)
    success, failed = 0, 0

    for uid in user_ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
            success += 1
            await asyncio.sleep(0.05)
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except Exception as e:
            logger.error(f"Error sending advert to {uid}: {e}")
            failed += 1

    await callback.message.answer(translate(lang, "advert_sent", success=success, failed=failed))
    await state.clear()


@router.channel_post(F.chat.id == settings.CHANNEL_ID)
async def forward_channel_post(msg: Message, session: AsyncSession, bot: Bot):
    user_ids = await User.get_all_user_ids(session)
    success, failed = 0, 0

    for uid in user_ids:
        try:
            await bot.copy_message(chat_id=uid, from_chat_id=msg.chat.id, message_id=msg.message_id)
            success += 1
            await asyncio.sleep(0.05)
        except (TelegramForbiddenError, TelegramBadRequest):
            failed += 1
        except Exception as e:
            logger.error(f"Error forwarding channel post to {uid}: {e}")
            failed += 1

    logger.info(f"Forwarded channel post. Success: {success}, Failed: {failed}")
