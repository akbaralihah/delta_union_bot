import os
import random
import re

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Bot administratorlari
ADMINS = [1998050207, 5459394614, 5797855429]

load_dotenv()


# Google Sheets API ulanishi
def get_sheet_by_url(url_env_name: str):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
        client = gspread.authorize(creds)
        return client.open_by_url(os.getenv(url_env_name)).sheet1
    except Exception as e:
        print(f"{url_env_name} jadvaliga ulanishda xatolik: {e}")
        return None


CONTAINER_SHEET = get_sheet_by_url("CONTAINER_SHEET_URL")
CARGO_1_SHEET = get_sheet_by_url("CARGO_1_SHEET_URL")
CARGO_2_SHEET = get_sheet_by_url("CARGO_2_SHEET_URL")


def track(container_input: str) -> str:
    if CONTAINER_SHEET is None:
        return "Xatolik: Google Sheets ga ulanish imkonsiz."

    container_input = container_input.replace("#", "").strip().lower()
    if not container_input:
        return "❗ Kontayner raqami kiritilmagan."

    expected_headers = [
        "Client", "Factory", "Container №", "ChN Platform", "Product name",
        "Direction", "Dispatch", "Border", "Arrive", "Status", "Company name"
    ]

    try:
        rows = CONTAINER_SHEET.get_all_records(expected_headers=expected_headers)
    except gspread.exceptions.GSpreadException as e:
        return f"Xatolik: Ma'lumotlarni olishda muammo: {e}"

    if not rows:
        return "❗ Jadval bo‘sh yoki sarlavhalar mos kelmadi."

    for row in rows:
        container_number = str(row.get("Container №", "")).replace("#", "").strip().lower()
        if container_input == container_number:
            status = row.get("Status", "Noma'lum")
            match = re.search(r'(\d+)\s*км', status)
            if match:
                original_km = int(match.group(1))
                extra_km = random.randint(100, 450)
                status = re.sub(r'\d+\s*км', f'{original_km + extra_km} км', status)

            msg = f"""Hurmatli mijoz, assalomu alaykum!

👤 Mijoz: {row.get("Company name") or row.get("Client")}
📦 Mahsulot: {row.get("Product name", "—")}
🚋 Kontayner №: {row.get("Container №", "Noma'lum")}
🚦 Platforma: {row.get("ChN Platform", "—")}
🧭 Yo‘nalish: {row.get("Direction", "—")}
📍 Yetib kelish: {row.get("Arrive", "—")}
📌 Holat: {status}

Hurmat bilan, Delta Union Logistics
https://t.me/deltaunionlogistics"""
            return msg

    return "❗ Kontayner topilmadi."


def search_by_shipping_mark(query: str) -> str:
    if CARGO_1_SHEET is None:
        return "Xatolik: Google Sheets ga ulanish imkonsiz."

    try:
        headers = CARGO_1_SHEET.row_values(2)
        all_data = CARGO_1_SHEET.get_all_values()
    except gspread.exceptions.GSpreadException as e:
        return f"Xatolik: Ma'lumotlarni olishda muammo: {e}"

    if len(all_data) <= 2:
        return "❗Jadval bo‘sh."

    data = []
    for row in all_data[2:]:
        data.append({headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))})

    query = query.strip().lower()

    for row in data:
        if str(row.get("Shipping mark", "")).strip().lower() == query:
            emoji_map = {
                "Shipping mark": "📌",
                "Agent": "👤",
                "Name": "🧑‍🤝‍🧑",
                "Product Name": "📦",
                "Package": "📦",
                "Total cbm": "📏",
                "GW": "⚖️",
                "LCL/LTL": "🚚",
                "Warehouse": "📦",
                "Date of arrive at wh": "🗓️",
                "Loading to truck/cntr date": "🚛",
                "Status": "📍",
                "Arrive at Horgos or Kashgar": "🏁",
                "Date of arrive at destination": "🗓️",
                "Destination": "🌍"
            }

            result_lines = []
            for key, value in row.items():
                if not key:
                    continue
                if key in ["Agent", "Total cbm", "LCL/LTL", "Warehouse", "Loading to truck/cntr date"]:
                    continue
                emoji = emoji_map.get(key, "❓")
                label = f"{emoji} {key}: {value}"
                if key == "Name":
                    label = f"{emoji} {key}: {value} aka"
                result_lines.append(label)

            return "\n".join(result_lines) + """\n
Hurmat bilan, Delta Union Logistics
https://t.me/deltaunionlogistics"""

    return "🔍 Hech qanday mos Shipping Mark topilmadi."


def search_by_id_in_cargo_2(cargo_id: str) -> str:
    if CARGO_2_SHEET is None:
        return "Xatolik: Google Sheets ga ulanish imkonsiz."

    try:
        headers = CARGO_2_SHEET.row_values(2)
        all_data = CARGO_2_SHEET.get_all_values()
    except gspread.exceptions.GSpreadException as e:
        return f"Xatolik: Ma'lumotlarni olishda muammo: {e}"

    if len(all_data) <= 2:
        return "❗Jadval bo‘sh."

    data = []
    for row in all_data[2:]:
        data.append({headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))})

    cargo_id = cargo_id.strip()
    print(data)

    for row in data:
        if row.get("ID", "").strip() == cargo_id:
            client_name = row.get("Client Name", "—")
            phone = row.get("Telefon Nomer", "—")
            product = row.get("Product Name", "—")
            status = row.get("Status", "—")

            return f"""📦 Yuk ma'lumotlari:

👤 Mijoz: {client_name}
📞 Telefon: {phone}
🛒 Mahsulot: {product}
📌 Holat: {status}

Hurmat bilan, Delta Union Logistics
https://t.me/deltaunionlogistics"""

    return "❗ ID bo‘yicha hech qanday mos yuk topilmadi."
