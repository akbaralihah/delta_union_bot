import logging
from typing import Callable, Awaitable

from aiogram import Router, html, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.reply import main_menu_buttons, admin_menu_buttons, choice_search_menu_buttons
from bot.states import UserStates
from bot.translations import translate
from bot.utils import track, search_by_shipping_mark, search_cargo
from db.models import User
from settings import settings

logger = logging.getLogger(__file__)
router = Router()


async def process_cargo_search(
    msg: Message,
    state: FSMContext,
    session: AsyncSession,
    search_func: Callable[[str, str], Awaitable[dict]],
) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)

    response = await search_func(msg.text, lang)

    message_text = response.get("message", "Unknown status")
    await state.clear()

    if response.get("status") not in (200, 404):
        error_msg = (
            f"⚠ <b>Error:</b> {html.quote(message_text)}\n"
            f"👤 <b>From:</b> <a href='tg://user?id={msg.from_user.id}'>{html.quote(msg.from_user.full_name)}</a>"
        )
        try:
            await msg.bot.send_message(
                chat_id=response.get("reception"),
                text=error_msg,
                parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            logger.error(
                f"Failed to send error to group {response.get('reception')}: {e}"
            )

    reply_markup = (
        admin_menu_buttons(lang)
        if msg.from_user.id in settings.ADMINS
        else main_menu_buttons(lang)
    )
    await msg.reply(
        text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
    )


@router.message(
    F.text.in_([translate("UZ", "search_cargo"), translate("RU", "search_cargo")])
)
async def search_command_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(
        text=translate(lang, "choose_search"),
        reply_markup=choice_search_menu_buttons(lang),
    )
    await state.set_state(UserStates.search_choice_menu)


@router.message(UserStates.search_choice_menu)
async def search_choice_cmd_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(translate(lang, "enter_cargo_number"))

    # Альтернатива: использование словаря вместо цепочки if/elif для большей чистоты
    state_mapping = {
        translate(lang, "full_container"): UserStates.full_container,
        translate(lang, "groupage_cargo"): UserStates.groupage_cargo_1,
        translate(lang, "cargo_tracking"): UserStates.groupage_cargo_2,
    }

    target_state = state_mapping.get(msg.text)
    if target_state:
        await state.set_state(target_state)


@router.message(UserStates.full_container)
async def container_number_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> None:
    await process_cargo_search(msg, state, session, track)


@router.message(UserStates.groupage_cargo_1)
async def cargo_number_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> None:
    await process_cargo_search(msg, state, session, search_by_shipping_mark)


@router.message(UserStates.groupage_cargo_2)
async def cargo_id_handler(
    msg: Message, state: FSMContext, session: AsyncSession
) -> None:
    await process_cargo_search(msg, state, session, search_cargo)
