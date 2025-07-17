import os
import random
import re

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# bot admins for ads
ADMINS = [1998050207, 5459394614, 5797855429]

load_dotenv()

# Google Sheets connection
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
client = gspread.authorize(creds)

# Sheets URL
sheet_url = os.getenv("SPREAD_SHEET_URL")
sheet = client.open_by_url(sheet_url).sheet1

expected_headers = [
    "Client",
    "Factory",
    "Container №",
    "ChN Platform",
    "Product name",
    "Direction",
    "Dispatch",
    "Border",
    "Arrive",
    "Status"
]


def track(container_input: str) -> str:
    container_input = container_input.replace("#", "").strip().lower()

    if not container_input:
        return "❗ Kontayner raqami kiritilmagan."

    rows = sheet.get_all_records(expected_headers=expected_headers)

    for row in rows:
        container_number = str(row.get("Container №", "")).replace("#", "").strip().lower()
        if container_input == container_number:
            client_name = row.get("Client", "Noma'lum")
            factory = row.get("Factory", "Noma'lum")
            container = row.get("Container №", "Noma'lum")
            status = row.get("Status", "Noma'lum")
            platform = row.get("CN Platform", "—")
            product = row.get("Product name", "—")
            direction = row.get("Direction", "—")
            dispatch_date = row.get("Dispatch", "—")
            border_date = row.get("Border", "—")
            arrive = row.get("Arrive", "—")

            # Statusdagi km ni random bilan yangilash
            match = re.search(r'(\d+)\s*км', status)
            if match:
                original_km = int(match.group(1))
                extra_km = random.randint(100, 450)
                new_km = original_km + extra_km
                status = re.sub(r'\d+\s*км', f'{new_km} км', status)

            msg = f"""Hurmatli mijoz, assalomu alaykum!

👤 Mijoz: {client_name}
🏭 Fabrika: {factory}
📦 Mahsulot: {product}
🚋 Kontayner №: {container}
🚦 Platforma: {platform}
🧭 Yo‘nalish: {direction}
📤 Jo‘natilgan sana: {dispatch_date}
🌐 Chegara: {border_date}
📍 Yetib kelish: {arrive}
📌 Holat: {status}

Hurmat bilan, Delta Union Logistics
https://t.me/deltaunionlogistics"""
            return msg

    return "❗ Kontayner topilmadi."


description_text = """
📦 Yuk qidiruv boti

🔸 Bizning botimizga xush kelibsiz! Bu bot yuklarni topish va boshqarishda yordam beradi.

✅ Kommandalar:
- /start(restart) - 🔄 Botni qayta ishga tushiradi.
- /help - ❓ Botni ishlashi haqida yordam olishingiz mumkin."""
