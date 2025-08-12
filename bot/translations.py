LANG = {
    "UZ": {
        "greeting": "😊 Assalomu alaykum",
        "start_command": "🔄 Botni ishga tushirish",
        "restart_command": "♻️ Botni qayta ishga tushirish",
        "help_command": "❓ Yordam",
        "search_menu": {
            "search_btn": "🔎 Yukni qidirish",
            "full_container": "📦 To'liq konteyner/Fura",
            "groupage": "🧩 Yig'ma yuklar",
            "cargo_tracking": "🚚 Cargo tracking",
            "choose_section": "Qidiruv uchun bo'limni tanlang👇"
        },
        "admin_menu": {
            "search_btn": "🔎 Konteyner/Fura qidirish",
            "advert": "📢 Reklama"
        },
        "advert": {
            "no_permission": "❌ Sizda bu amalni bajarishga ruxsat yo'q.",
            "send_text": "📨 Reklama matnini yuboring (matn, rasm, video yoki gif bo‘lishi mumkin):",
            "unknown_type": "❌ Noma'lum kontent turi. Faqat matn, rasm, video yoki gif yuboring.",
            "cancelled": "❌ Reklama yuborilishi bekor qilindi.",
            "sent": "✅ Reklama yuborildi.\n📨 Qabul qilinganlar: {success}\n❌ Xatoliklar: {failed}"
        }
    },
    "RU": {
        "greeting": "😊 Здравствуйте",
        "start_command": "🔄 Запустить бота",
        "restart_command": "♻️ Перезапустить бота",
        "help_command": "❓ Помощь",
        "search_menu": {
            "search_btn": "🔎 Поиск груза",
            "full_container": "📦 Полный контейнер/фура",
            "groupage": "🧩 Сборные грузы",
            "cargo_tracking": "🚚 Отслеживание груза",
            "choose_section": "Выберите раздел для поиска👇"
        },
        "admin_menu": {
            "search_btn": "🔎 Поиск контейнера/фуры",
            "advert": "📢 Реклама"
        },
        "advert": {
            "no_permission": "❌ У вас нет прав на это действие.",
            "send_text": "📨 Отправьте текст рекламы (может быть текст, фото, видео или gif):",
            "unknown_type": "❌ Неизвестный тип контента. Отправьте только текст, фото, видео или gif.",
            "cancelled": "❌ Отправка рекламы отменена.",
            "sent": "✅ Реклама отправлена.\n📨 Доставлено: {success}\n❌ Ошибки: {failed}"
        }
    }
}


def t(lang: str, key_path: str, **kwargs) -> str:
    keys = key_path.split(".")
    text = LANG[lang]
    for k in keys:
        text = text[k]
    return text.format(**kwargs)


description_text = """
📦 Yuk qidiruv boti

🔸 Bizning botimizga xush kelibsiz! Bu bot yuklarni topish va boshqarishda yordam beradi.

✅ Kommandalar:
- /start(restart) - 🔄 Botni qayta ishga tushiradi.
- /help - ❓ Botni ishlashi haqida yordam olishingiz mumkin."""
