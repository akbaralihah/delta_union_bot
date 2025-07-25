from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def main_menu_buttons():
    btn1 = KeyboardButton(text="🔎 Yukni qidirish")
    btn2 = KeyboardButton(text="👤 Admin")
    design = [
        [btn1],
        [btn2]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True, one_time_keyboard=True)


def choice_search_menu_buttons():
    btn1 = KeyboardButton(text="📦 Shaxsiy konteyner")
    btn2 = KeyboardButton(text="🧩 Yig'ma konteyner")
    design = [
        [btn1],
        [btn2]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True, one_time_keyboard=True)


def admin_menu_buttons():
    btn1 = KeyboardButton(text="🔎 Yukni qidirish")
    btn2 = KeyboardButton(text="📢 Reklama")
    design = [
        [btn1],
        [btn2]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True, one_time_keyboard=True)


def confirm_keyboard():
    btn1 = InlineKeyboardButton(text="✅ Ha", callback_data="confirm_send")
    btn2 = InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel_send")
    design = [
        [btn1, btn2]
    ]
    return InlineKeyboardMarkup(inline_keyboard=design)
