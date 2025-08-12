from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from bot.translations import t


def language_keyboard():
    btn1 = InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="set_lang_UZ")
    btn2 = InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_RU")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn1],
            [btn2]
        ]
    )


def main_menu_buttons(lang="UZ"):
    btn1 = KeyboardButton(text=t(lang, "search_cargo"))
    btn2 = KeyboardButton(text=t(lang, "admin"))
    return ReplyKeyboardMarkup(
        keyboard=[
            [btn1],
            [btn2]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def choice_search_menu_buttons(lang="UZ"):
    btn1 = KeyboardButton(text=t(lang, "full_container"))
    btn2 = KeyboardButton(text=t(lang, "groupage_cargo"))
    btn3 = KeyboardButton(text=t(lang, "cargo_tracking"))
    return ReplyKeyboardMarkup(
        keyboard=[
            [btn1],
            [btn2],
            [btn3],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def admin_menu_buttons(lang="UZ"):
    btn1 = KeyboardButton(text=t(lang, "search_container"))
    btn2 = KeyboardButton(text=t(lang, "advert"))
    return ReplyKeyboardMarkup(
        keyboard=[
            [btn1],
            [btn2]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def confirm_keyboard(lang="UZ"):
    btn1 = InlineKeyboardButton(text=t(lang, "yes"), callback_data="confirm_send")
    btn2 = InlineKeyboardButton(text=t(lang, "no"), callback_data="cancel_send")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [btn1, btn2]
        ]
    )
