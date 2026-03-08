from aiogram import Router, html, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.reply import (
    main_menu_buttons,
    admin_menu_buttons,
    choice_search_menu_buttons
)
from bot.states import UserStates
from bot.translations import translate
from bot.utils import track, search_by_shipping_mark, search_cargo
from db.models import User
from settings import settings

router = Router()


@router.message(F.text.in_([translate("UZ", "search_cargo"), translate("RU", "search_cargo")]))
async def search_command_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(
        text=translate(lang, "choose_search"),
        reply_markup=choice_search_menu_buttons(lang)
    )
    await state.set_state(UserStates.search_choice_menu)


@router.message(UserStates.search_choice_menu)
async def search_choice_cmd_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(translate(lang, "enter_cargo_number"))
    if msg.text == translate(lang, "full_container"):
        await state.set_state(UserStates.full_container)
    elif msg.text == translate(lang, "groupage_cargo"):
        await state.set_state(UserStates.groupage_cargo_1)
    elif msg.text == translate(lang, "cargo_tracking"):
        await state.set_state(UserStates.groupage_cargo_2)


@router.message(UserStates.full_container)
async def container_number_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    response = await track(msg.text, lang)
    message_text = response.get("message")
    await state.clear()

    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ <b>Error:</b> {html.quote(response['message'])}\n"
                 f"👤 <b>From:</b> <a href='tg://user?id={msg.from_user.id}'>{html.quote(msg.from_user.full_name)}</a>",
            parse_mode=ParseMode.HTML
        )

    reply_markup = admin_menu_buttons(lang) if msg.from_user.id in settings.ADMINS else main_menu_buttons(lang)
    await msg.reply(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@router.message(UserStates.groupage_cargo_1)
async def cargo_number_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    response = await search_by_shipping_mark(msg.text, lang)
    message_text = response["message"]
    await state.clear()

    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ <b>Error:</b> {html.quote(response['message'])}\n"
                 f"👤 <b>From:</b> <a href='tg://user?id={msg.from_user.id}'>{html.quote(msg.from_user.full_name)}</a>",
            parse_mode=ParseMode.HTML
        )

    reply_markup = admin_menu_buttons(lang) if msg.from_user.id in settings.ADMINS else main_menu_buttons(lang)
    await msg.reply(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@router.message(UserStates.groupage_cargo_2)
async def cargo_id_handler(msg: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    response = await search_cargo(msg.text, lang)
    message_text = response["message"]
    await state.clear()

    if response["status"] != 200:
        await msg.bot.send_message(
            response["reception"],
            text=f"⚠ <b>Error:</b> {html.quote(response['message'])}\n"
                 f"👤 <b>From:</b> <a href='tg://user?id={msg.from_user.id}'>{html.quote(msg.from_user.full_name)}</a>",
            parse_mode=ParseMode.HTML
        )

    reply_markup = admin_menu_buttons(lang) if msg.from_user.id in settings.ADMINS else main_menu_buttons(lang)
    await msg.reply(text=message_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
