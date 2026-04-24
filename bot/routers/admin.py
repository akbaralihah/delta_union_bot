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

from bot.reply import main_menu_buttons, admin_menu_buttons, confirm_keyboard
from bot.states import UserStates
from bot.translations import translate
from db.models import User
from settings import settings

router = Router()
logger = logging.getLogger(__name__)

# Temporary storage for collecting media group messages before processing
MEDIA_GROUP_MESSAGES: dict[str, list[Message]] = {}
MEDIA_GROUP_TASKS: dict[str, asyncio.Task] = {}


async def safe_copy_message(
    bot: Bot, chat_id: int, from_chat_id: int, message_id: int
) -> bool:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.copy_message(
                chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id
            )
            return True
        except TelegramForbiddenError:
            return False
        except TelegramBadRequest as e:
            logger.warning(f"Bad Request for user {chat_id}: {e}")
            return False
        except TelegramRetryAfter as e:
            logger.warning(
                f"Flood limit exceeded. Sleeping for {e.retry_after} seconds."
            )
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(
                    f"Failed to send to {chat_id} after {max_retries} attempts: {e}"
                )
                return False
            await asyncio.sleep(1)
    return False


async def safe_copy_messages(
    bot: Bot, chat_id: int, from_chat_id: int, message_ids: list[int]
) -> bool:
    max_retries = 3
    for attempt in range(max_retries):
        try:
            await bot.copy_messages(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_ids=message_ids,
            )
            return True
        except TelegramForbiddenError:
            return False
        except TelegramBadRequest as e:
            logger.warning(f"Bad Request for user {chat_id}: {e}")
            return False
        except TelegramRetryAfter as e:
            logger.warning(
                f"Flood limit exceeded. Sleeping for {e.retry_after} seconds."
            )
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(
                    f"Failed to send to {chat_id} after {max_retries} attempts: {e}"
                )
                return False
            await asyncio.sleep(1)
    return False


async def _flush_media_group(
    group_id: str,
    state: FSMContext,
    lang: str,
    bot: Bot,
) -> None:
    # Wait for all messages in the album to arrive
    await asyncio.sleep(0.7)

    messages = MEDIA_GROUP_MESSAGES.pop(group_id, [])
    MEDIA_GROUP_TASKS.pop(group_id, None)
    if not messages:
        return

    messages.sort(key=lambda m: m.message_id)
    msg_ids = [m.message_id for m in messages]
    chat_id = messages[0].chat.id

    await state.update_data(
        advert_msg_ids=msg_ids,
        advert_chat_id=chat_id,
        is_media_group=True,
    )

    # Preview the album as-is
    await bot.copy_messages(
        chat_id=chat_id,
        from_chat_id=chat_id,
        message_ids=msg_ids,
    )
    await messages[0].answer(
        translate(lang, "confirm_advert"),
        reply_markup=confirm_keyboard(lang),
    )


@router.message(F.text.in_([translate("UZ", "admin"), translate("RU", "admin")]))
async def admin_command_handler(msg: Message, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    answer_text = "https://t.me/Mr_bob0921"

    if msg.from_user.id in settings.ADMINS:
        await msg.answer(text=answer_text, reply_markup=admin_menu_buttons(lang))
    else:
        await msg.answer(text=answer_text, reply_markup=main_menu_buttons(lang))


@router.message(F.text.in_([translate("UZ", "advert"), translate("RU", "advert")]))
async def advert_command_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> Message | None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)

    if msg.from_user.id not in settings.ADMINS:
        return await msg.answer(translate(lang, "no_permission"))

    await msg.answer(translate(lang, "send_advert"))
    await state.set_state(UserStates.advert)
    return None


@router.message(UserStates.advert)
async def preview_advert_handler(
    msg: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)

    if msg.media_group_id:
        group_id = msg.media_group_id
        if group_id not in MEDIA_GROUP_MESSAGES:
            MEDIA_GROUP_MESSAGES[group_id] = []
        MEDIA_GROUP_MESSAGES[group_id].append(msg)

        # Reset the flush timer so it fires after the last message arrives
        if group_id in MEDIA_GROUP_TASKS:
            MEDIA_GROUP_TASKS[group_id].cancel()
        MEDIA_GROUP_TASKS[group_id] = asyncio.create_task(
            _flush_media_group(group_id, state, lang, bot)
        )
        return

    await state.update_data(
        advert_msg_id=msg.message_id,
        advert_chat_id=msg.chat.id,
        is_media_group=False,
    )
    reply_markup = confirm_keyboard(lang)
    if msg.text:
        await msg.answer(msg.text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif msg.photo:
        await msg.answer_photo(
            msg.photo[-1].file_id,
            caption=msg.caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    elif msg.video:
        await msg.answer_video(
            msg.video.file_id,
            caption=msg.caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    elif msg.animation:
        await msg.answer_animation(
            msg.animation.file_id,
            caption=msg.caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await msg.answer(translate(lang, "unknown_content"))


@router.callback_query(F.data.in_(["confirm_send", "cancel_send"]))
async def send_advert_to_all(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
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
    is_media_group = data.get("is_media_group", False)
    chat_id = data.get("advert_chat_id")
    user_ids = await User.get_all_user_ids(session)
    success, failed = 0, 0

    await callback.message.answer("⏳ Рассылка началась, это может занять время...")

    if is_media_group:
        msg_ids = data.get("advert_msg_ids", [])
        for uid in user_ids:
            is_sent = await safe_copy_messages(bot, uid, chat_id, msg_ids)
            if is_sent:
                success += 1
            else:
                failed += 1
            await asyncio.sleep(0.05)
    else:
        msg_id = data.get("advert_msg_id")
        for uid in user_ids:
            is_sent = await safe_copy_message(bot, uid, chat_id, msg_id)
            if is_sent:
                success += 1
            else:
                failed += 1
            await asyncio.sleep(0.05)

    await callback.message.answer(
        translate(lang, "advert_sent", success=success, failed=failed)
    )
    await state.clear()


@router.channel_post(F.chat.id == settings.CHANNEL_ID)
async def forward_channel_post(msg: Message, session: AsyncSession, bot: Bot):
    user_ids = await User.get_all_user_ids(session)
    success, failed = 0, 0

    for uid in user_ids:
        is_sent = await safe_copy_message(bot, uid, msg.chat.id, msg.message_id)
        if is_sent:
            success += 1
        else:
            failed += 1

        await asyncio.sleep(0.05)

    logger.info(f"Forwarded channel post. Success: {success}, Failed: {failed}")
