LANG = {
    "UZ": {
        "greeting": "😊 Assalomu alaykum, {name}!",
        "change_language": "🌐 Tilni o‘zgartirish",
        "choose_language": "🌍 Iltimos, tilni tanlang:",
        "start_command": "🔄 Botni ishga tushirish",
        "restart_command": "♻️ Botni qayta ishga tushirish",
        "help_command": "❓ Yordam",
        "main_menu": "📋 Asosiy menyu",
        "search_cargo": "🔍 Yukni qidirish",
        "choose_search": "📌 Qidiruv turini tanlang:",
        "full_container": "📦 To‘liq konteyner / Fura",
        "groupage_cargo": "🧩 Yig‘ma yuk",
        "cargo_tracking": "🚚 Cargo yukini kuzatish",
        "enter_cargo_number": "✏️ Yuk raqamini kiriting:",
        "admin": "⚙️ Admin",
        "advert": "📢 Reklama",
        "no_permission": "❌ Sizda bu amalni bajarishga ruxsat yo‘q.",
        "send_advert": "📨 Reklama matnini yuboring (matn, rasm, video yoki gif bo‘lishi mumkin):",
        "unknown_content": "❌ Noma’lum kontent turi. Faqat matn, rasm, video yoki gif yuboring.",
        "advert_cancelled": "❌ Reklama yuborilishi bekor qilindi.",
        "advert_sent": "✅ Reklama yuborildi.\n📨 Qabul qilinganlar: {success}\n❌ Xatoliklar: {failed}",
        "lang_updated": "✅ Til saqlandi.",
        "yes": "✅ Ha",
        "no": "❌ Yo'q",
    },
    "RU": {
        "greeting": "😊 Здравствуйте, {name}!",
        "change_language": "🌐 Изменить язык",
        "choose_language": "🌍 Пожалуйста, выберите язык:",
        "start_command": "🔄 Запустить бота",
        "restart_command": "♻️ Перезапустить бота",
        "help_command": "❓ Помощь",
        "main_menu": "📋 Главное меню",
        "search_cargo": "🔍 Поиск груза",
        "choose_search": "📌 Выберите тип поиска:",
        "full_container": "📦 Полный контейнер / Фура",
        "groupage_cargo": "🧩 Сборный груз",
        "cargo_tracking": "🚚 Отслеживание карго груза",
        "enter_cargo_number": "✏️ Введите номер груза:",
        "admin": "⚙️ Админ",
        "advert": "📢 Реклама",
        "no_permission": "❌ У вас нет прав на это действие.",
        "send_advert": "📨 Отправьте текст рекламы (может быть текст, фото, видео или gif):",
        "unknown_content": "❌ Неизвестный тип контента. Отправьте только текст, фото, видео или gif.",
        "advert_cancelled": "❌ Отправка рекламы отменена.",
        "advert_sent": "✅ Реклама отправлена.\n📨 Доставлено: {success}\n❌ Ошибки: {failed}",
        "lang_updated": "✅ Язык успешно сохранен.",
        "yes": "✅ Да",
        "no": "❌ Нет",
    }
}


def translate(lang: str, key_path: str, **kwargs) -> str:
    keys = key_path.split(".")
    text = LANG[lang]
    for k in keys:
        text = text[k]
    return text.format(**kwargs)


description_text = {
    "UZ": """
📦 *Yuk qidiruv boti*

🔸 Bizning botimizga xush kelibsiz! Bu bot sizga yuklarni topish va boshqarishda yordam beradi.

✅ *Komandalar:*
- `/start` yoki `/restart` — 🔄 Botni ishga tushirish yoki qayta ishga tushirish
- `/help` — ❓ Yordam olish
""",
    "RU": """
📦 *Бот поиска грузов*

🔸 Добро пожаловать в наш бот! Он поможет вам находить и отслеживать грузы.

✅ *Команды:*
- `/start` или `/restart` — 🔄 Запустить или перезапустить бота
- `/help` — ❓ Получить помощь
"""
}
