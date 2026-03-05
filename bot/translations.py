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
        "choose_search": "🔍 Qidiruv turini tanlang:",
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
        "message": {
            "date": "🗓 Sana",
            "header": "Hurmatli mijoz, assalomu alaykum!",
            "footer": "Hurmat bilan, Delta Union Logistics\nhttps://t.me/deltaunionlogistics",
            "waiting_for_data": "Ma'lumotlar kutilmoqda",
            "full_container": {
                "company_name": "🏢 Korxona nomi",
                "product_name": "📦 Yuk nomi",
                "container_id": "🚋 Konteyner raqami",
                "platform_id": "🚦 Platforma raqami",
                "status": "📌 Holati",
            },
            "groupage_cargo": {
                "shipping_mark": "📌 Shipping mark",
                "name": "👤 Ismi",
                "product_name": "📦 Yuk nomi",
                "package": "🎁 O‘ram",
                "total_cbm": "📏 Umumiy hajm (cbm)",
                "date_of_arrive": "🗓 Yetib kelgan sana",
                "status": "📌 Holati",
                "destination": "🌍 Manzil",
            },
            "cargo_tracking": {
                "info": "📦 Yuk ma'lumotlari:",
                "id": "🆔 Yuk ID:",
                "client_name": "👤 Mijoz ismi:",
                "phone_number": "📞 Telefon raqami:",
                "product_name": "📦 Mahsulot nomi:",
                "gross_weight": "⚖ Brutto vazn:",
                "status": "📊 Holati:"
            }
        }
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
        "choose_search": "🔍 Выберите тип поиска:",
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
        "message": {
            "date": "🗓 Дата",
            "header": "Уважаемый клиент, здравствуйте!",
            "footer": "С уважением, Delta Union Logistics\nhttps://t.me/deltaunionlogistics",
            "waiting_for_data": "Данные ожидаются",
            "full_container": {
                "company_name": "🏢 Название компании",
                "product_name": "📦 Наименование груза",
                "container_id": "🚋 Номер контейнера",
                "platform_id": "🚦 Номер платформы",
                "status": "📌 Статус"
            },
            "groupage_cargo": {
                "shipping_mark": "📌 Shipping mark",
                "name": "👤 Имя",
                "product_name": "📦 Наименование груза",
                "package": "🎁 Упаковка",
                "total_cbm": "📏 Общий объем (cbm)",
                "date_of_arrive": "🗓 Дата прибытия",
                "status": "📌 Статус",
                "destination": "🌍 Пункт назначения",
            },
            "cargo_tracking": {
                "info": "📦 Информация о грузе:",
                "id": "🆔 ID груза:",
                "client_name": "👤 Имя клиента:",
                "phone_number": "📞 Номер телефона:",
                "product_name": "📦 Название товара:",
                "gross_weight": "⚖ Вес брутто:",
                "status": "📊 Статус:"
            }
        }
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
