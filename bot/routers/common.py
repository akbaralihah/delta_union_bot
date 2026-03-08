from aiogram import Router, html, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.reply import (
    main_menu_buttons,
    admin_menu_buttons,
    language_keyboard
)
from bot.translations import translate
from db.models import User
from settings import settings

router = Router()


@router.message(Command(commands=["start", "restart"]))
async def command_start_handler(msg: Message, session: AsyncSession) -> None:
    user = await User.get_by_user_id(msg.from_user.id, session=session)

    if not user:
        await User.upsert(
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
    answer_text = translate(lang, "greeting", name=f"<b>{html.quote(msg.from_user.full_name)}</b>")

    if msg.from_user.id in settings.ADMINS:
        await msg.answer(answer_text, reply_markup=admin_menu_buttons(lang), parse_mode=ParseMode.HTML)
    else:
        await msg.answer(answer_text, reply_markup=main_menu_buttons(lang), parse_mode=ParseMode.HTML)


@router.message(F.text.in_([translate("UZ", "change_language"), translate("RU", "change_language")]))
async def change_language(msg: Message, session: AsyncSession):
    lang = await User.get_user_lang(msg.from_user.id, session=session)
    await msg.answer(
        translate(lang, "choose_language"),
        reply_markup=language_keyboard(lang)
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(call: CallbackQuery, session: AsyncSession):
    lang = call.data.split("_")[-1]
    await User.update_user_lang(call.from_user.id, lang, session=session)
    await call.message.edit_text(translate(lang, "lang_updated"))
    
    if call.from_user.id in settings.ADMINS:
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
