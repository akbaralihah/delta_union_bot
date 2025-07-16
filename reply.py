from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu_buttons():
    btn1 = KeyboardButton(text="🔎 Yukni qidirish")
    btn2 = KeyboardButton(text="📃 Foydalanish bo'yicha yo'riqnoma")
    btn3 = KeyboardButton(text="👤 Admin")
    design = [
        [btn1],
        [btn2],
        [btn3]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True, one_time_keyboard=True)
