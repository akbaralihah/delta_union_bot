import os
from datetime import datetime

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

from bot.translations import translate

# Bot administrators
ADMINS = [1998050207, 5459394614, 5797855429]

load_dotenv()


# Google Sheets API connection
def get_sheet_by_url(url_env_name: str):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_PATH"), scope)
        client = gspread.authorize(creds)
        return client.open_by_url(os.getenv(url_env_name)).sheet1
    except Exception as e:
        print(f"Unable to connect the table {url_env_name}: {e}")
        return None


CONTAINER_SHEET = get_sheet_by_url("CONTAINER_SHEET_URL")
CARGO_1_SHEET = get_sheet_by_url("CARGO_1_SHEET_URL")
CARGO_2_SHEET = get_sheet_by_url("CARGO_2_SHEET_URL")


def track(user_input: str, lang: str) -> dict:
    response = {
        "status": 404,
        "message": "Container not found.",
        "reception": ADMINS[0]
    }
    if CONTAINER_SHEET is None:
        response["message"] = "Error: Unable to connect Google Sheets."
        return response

    user_input = user_input.replace("#", "").strip().lower()
    if not user_input:
        response["message"] = "Container number not entered."
        return response

    expected_headers = [
        "Client", "Factory", "Container №", "ChN Platform", "Product name",
        "Direction", "Dispatch", "Border", "Arrive", "Status", "Company name",
        "Fake status"
    ]

    try:
        rows = CONTAINER_SHEET.get_all_records(expected_headers=expected_headers)
    except gspread.exceptions.GSpreadException as e:
        response.update({
            "status": "400",
            "message": f"Error: Problem retrieving data: {e}"
        })
        return response

    if not rows:
        response.update({
            "status": "400",
            "message": "The table is empty or the headings do not match."
        })
        return response

    for row in rows:
        container_id = str(row.get("Container №", "")).replace("#", "").strip().lower()
        data = {}
        if user_input == container_id:
            status = row.get("Fake status", "-")
            if status.isdigit():
                status += "km"
            data.update({
                "company_name": row.get("Company name").strip() or row.get("Client").strip(),
                "product_name": row.get("Product name").strip(),
                "container_id": container_id.strip(),
                "platform_id": str(row.get("KZ Platform")).strip() or str(row.get("ChN Platform")).strip(),
                "status": status.strip()
            })

            reply_message = f"*{translate(lang, 'message.header')}*\n\n"
            for key, value in data.items():
                if not value:
                    continue
                label = translate(lang, f"message.full_container.{key}")
                reply_message += f"*{label}:* `{value}`\n"
            reply_message += f"*{translate(lang, 'message.date')}*: `{datetime.now().strftime("%d-%m-%Y")}`"
            reply_message += f"\n\n*{translate(lang, 'message.footer')}*"
            response.update({
                "status": 200,
                "message": reply_message,
            })
            return response

    return response


def search_by_shipping_mark(user_input: str, lang: str) -> dict:
    response = {
        "status": 404,
        "message": "Container not found.",
        "reception": ADMINS[0]
    }

    if CARGO_1_SHEET is None:
        response["message"] = "Error: Unable to connect Google Sheets."
        return response

    try:
        headers = CARGO_1_SHEET.row_values(2)
        all_data = CARGO_1_SHEET.get_all_values()
    except gspread.exceptions.GSpreadException as e:
        response.update({
            "status": 400,
            "message": f"Error: Problem retrieving data: {e}"
        })
        return response

    if len(all_data) <= 2:
        response.update({
            "status": 400,
            "message": "Error: The table is empty."
        })
        return response

    data = []
    for row in all_data[2:]:
        data.append({headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))})


    user_input = user_input.strip().lower()

    for row in data:
        if str(row.get("Shipping mark", "")).strip().lower() == user_input.strip().lower():
            cargo_data = {
                "shipping_mark": row.get("Shipping mark", "").strip(),
                "name": row.get("Name", "").strip(),
                "product_name": row.get("Product Name", "").strip(),
                "package": row.get("Package", "").strip(),
                "total_cbm": row.get("Total cbm", "").strip(),
                "date_of_arrive": row.get("Date of arrive at destination", "").strip(),
                "status": row.get("Status", "").strip(),
                "destination": row.get("Destination", "").strip(),
            }

            reply_message = f"*{translate(lang, 'message.header')}*\n\n"
            for key, value in cargo_data.items():
                if not value:
                    continue
                label = translate(lang, f"message.groupage_cargo.{key}")
                reply_message += f"*{label}:* `{value}`\n"
            reply_message += f"*{translate(lang, 'message.date')}*: `{datetime.now().strftime("%d-%m-%Y")}`"
            reply_message += f"\n\n*{translate(lang, 'message.footer')}*"

            response.update({
                "status": 200,
                "message": reply_message
            })
            return response

    return response


def search_cargo(cargo_id: str, lang: str) -> dict:
    response = {
        "status": 404,
        "message": "Container not found.",
        "reception": ADMINS[0]
    }

    if CARGO_2_SHEET is None:
        response["message"] = "Error: Unable to connect Google Sheets."
        return response

    try:
        headers = CARGO_2_SHEET.row_values(2)
        all_data = CARGO_2_SHEET.get_all_values()
    except gspread.exceptions.GSpreadException as e:
        response.update({
            "status": 400,
            "message": f"Error: Problem retrieving data: {e}"
        })
        return response

    if len(all_data) <= 2:
        response.update({
            "status": 400,
            "message": "Table is empty."
        })
        return response

    data = []
    for row in all_data[2:]:
        data.append({headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))})

    cargo_id = cargo_id.strip()

    for row in data:
        if row.get("ID", "").strip() == cargo_id:
            cargo_data = {
                "id": cargo_id,
                "client_name": row.get("Client Name", "—"),
                "phone_number": row.get("Telefon Nomer", "—"),
                "product_name": row.get("Product Name", "—"),
                "gross_weight": row.get("GW", "—"),
                "status": row.get("Status", "—")
            }

            reply_message = f"*{translate(lang, 'message.header')}*\n\n"
            for key, value in cargo_data.items():
                if not value:
                    continue
                label = translate(lang, f"message.cargo_tracking.{key}")
                reply_message += f"*{label}:* `{value}`\n"
            reply_message += f"*{translate(lang, 'message.date')}*: `{datetime.now().strftime("%d-%m-%Y")}`"
            reply_message += f"\n\n*{translate(lang, 'message.footer')}*"

            response.update({
                "status": 200,
                "message": reply_message
            })
            return response

    return response
