import os
import random
import re

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# for bot admins
ADMINS = [1998050207, 5459394614, 5797855429]

load_dotenv()

try:
    # Google Sheets API ga ulanish
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
    client = gspread.authorize(creds)

    CONTAINER_SHEET_URL = os.getenv("CONTAINER_SHEET_URL")
    CARGO_SHEET_URL = os.getenv("CARGO_SHEET_URL")

    CONTAINER_SHEET = client.open_by_url(CONTAINER_SHEET_URL).sheet1
    CARGO_SHEET = client.open_by_url(CARGO_SHEET_URL).sheet1
except Exception as e:
    print(f"Google Sheets ga ulanishda xatolik yuz berdi: {e}")
    sheet = None


def track(container_input: str) -> str:
    sheet = CONTAINER_SHEET

    if sheet is None:
        return "Xatolik: Google Sheets ga ulanish imkonsiz."

    container_input = container_input.replace("#", "").strip().lower()

    if not container_input:
        return "❗ Kontayner raqami kiritilmagan."

    expected_headers_for_track = [
        "Client", "Factory", "Container №", "ChN Platform", "Product name",
        "Direction", "Dispatch", "Border", "Arrive", "Status"
    ]

    try:
        rows = sheet.get_all_records(expected_headers=expected_headers_for_track)
    except gspread.exceptions.GSpreadException as e:
        return f"Xatolik: Ma'lumotlarni yuklashda muammo yuz berdi: {e}"

    if not rows:
        return "❗ Jadval bo‘sh yoki sarlavhalar mos kelmadi."

    for row in rows:
        container_number = str(row.get("Container №", "")).replace("#", "").strip().lower()
        if container_input == container_number:
            client_name = row.get("Client", "Noma'lum")
            factory = row.get("Factory", "Noma'lum")
            container = row.get("Container №", "Noma'lum")
            status = row.get("Status", "Noma'lum")
            platform = row.get("ChN Platform", "—")
            product = row.get("Product name", "—")
            direction = row.get("Direction", "—")
            dispatch_date = row.get("Dispatch", "—")
            border_date = row.get("Border", "—")
            arrive = row.get("Arrive", "—")

            match = re.search(r'(\d+)\s*км', status)
            if match:
                original_km = int(match.group(1))
                extra_km = random.randint(100, 450)
                new_km = original_km + extra_km
                status = re.sub(r'\d+\s*км', f'{new_km} км', status)

            msg = f"""Hurmatli mijoz, assalomu alaykum!

👤 Mijoz: {client_name} aka
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


def search_by_shipping_mark(query: str) -> str:
    sheet = CARGO_SHEET

    if sheet is None:
        return "Xatolik: Google Sheets ga ulanish imkonsiz."

    try:
        headers = sheet.row_values(2)
        all_data = sheet.get_all_values()

        data = []
        for row_values in all_data[2:]:
            row_dict = {}
            for i, header in enumerate(headers):
                if header:
                    try:
                        row_dict[header] = row_values[i]
                    except IndexError:
                        row_dict[header] = ""
            data.append(row_dict)

    except gspread.exceptions.GSpreadException as e:
        return f"Xatolik: Ma'lumotlarni yuklashda muammo yuz berdi: {e}"

    if not data:
        return "❗Jadval bo‘sh."

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

    for row in data:
        if str(row.get("Shipping mark", "")).strip().lower() == query.strip().lower():
            result_lines = []
            for key, value in row.items():
                if key:
                    emoji = emoji_map.get(key, "❓")
                    if key == "Name":
                        result_lines.append(f"{emoji} {key}: {value} aka")
                    else:
                        result_lines.append(f"{emoji} {key}: {value}")

            return "\n".join(result_lines[1:]) + """\n
Hurmat bilan, Delta Union Logistics
https://t.me/deltaunionlogistics"""

    return "🔍 Hech qanday mos Shipping Mark topilmadi."
