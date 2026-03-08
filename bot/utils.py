import html
import logging
from datetime import datetime
from typing import Optional, Dict, Callable

import gspread
from gspread.exceptions import GSpreadException

from bot.translations import translate
from settings import env

# Настраиваем логирование вместо обычного print()
logger = logging.getLogger(__name__)

ADMINS = [1998050207, 5459394614, 5797855429]


class GoogleSheetsManager:

    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self._client: Optional[gspread.Client] = None

    @property
    def client(self) -> gspread.Client:
        if self._client is None:
            try:
                self._client = gspread.service_account(filename=self.credentials_path)
            except Exception as e:
                logger.error(f"Google API Auth Error: {e}")
                raise
        return self._client

    def get_sheet(self, url: str) -> Optional[gspread.Worksheet]:
        try:
            return self.client.open_by_url(url).sheet1
        except Exception as e:
            logger.error(f"Cannot connect to table {url}: {e}")
            return None

    def find_row_by_value(
            self,
            sheet: Optional[gspread.Worksheet],
            search_value: str,
            header_row: int = 1
    ) -> Optional[
        Dict[str, str]]:
        if not sheet:
            return None

        try:
            cell = sheet.find(search_value, case_sensitive=False)
            if not cell or cell.row <= header_row:
                return None

            headers = sheet.row_values(header_row)
            row_data = sheet.row_values(cell.row)

            return {headers[i]: (row_data[i] if i < len(row_data) else "") for i in range(len(headers))}

        except GSpreadException as e:
            logger.error(f"GSpread search error: {e}")
            raise


gs_manager = GoogleSheetsManager(env.GOOGLE_CREDENTIALS_PATH)


def _build_response(status: int, message: str) -> dict:
    return {"status": status, "message": message, "reception": ADMINS[0]}


def _generate_html_reply(data: Dict[str, str], lang: str, category: str) -> str:
    reply = f"<b>{translate(lang, 'message.header')}</b>\n\n"

    for key, value in data.items():
        if not value or value == "—":
            continue
        label = translate(lang, f"message.{category}.{key}")
        reply += f"<b>{html.escape(label)}:</b> <code>{html.escape(str(value))}</code>\n"

    reply += f"<b>{translate(lang, 'message.date')}:</b> <code>{datetime.now().strftime('%d-%m-%Y')}</code>\n\n"
    reply += f"<b>{translate(lang, 'message.footer')}</b>"
    return reply


def _process_search(
        user_input: str,
        lang: str,
        sheet_url: str,
        header_row: int,
        category: str,
        data_mapper: Callable[[Dict[str, str]], Dict[str, str]]
) -> dict:
    if not user_input:
        return _build_response(400, "Input not entered.")

    sheet = gs_manager.get_sheet(sheet_url)
    if not sheet:
        return _build_response(500, "Error: Unable to connect to Google Sheets.")

    try:
        row = gs_manager.find_row_by_value(sheet, user_input, header_row=header_row)
    except GSpreadException as e:
        return _build_response(400, f"Error retrieving data: {e}")

    if not row:
        return _build_response(404, "Data not found.")

    # Используем переданную функцию-маппер для формирования нужного словаря
    data = data_mapper(row)

    reply_message = _generate_html_reply(data, lang, category)
    return _build_response(200, reply_message)


# ==========================================
# ЧИСТЫЕ ФУНКЦИИ-ОБРАБОТЧИКИ (Эндпоинты)
# ==========================================

def track(user_input: str, lang: str) -> dict:
    clean_input = user_input.replace("#", "").strip()

    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        status = row.get("Customer status")
        if not status:
            status = translate(lang, "message.waiting_for_data")
        if status.isdigit():
            status += "km"

        return {
            "product_name": row.get("Product name", "").strip(),
            "container_id": str(row.get("Container №", "")).replace("#", "").strip().upper(),
            "platform_id": str(row.get("KZ Platform", "") or row.get("ChN Platform", "")).strip(),
            "status": status.strip()
        }

    return _process_search(
        user_input=clean_input,
        lang=lang,
        sheet_url=env.CONTAINER_SHEET_URL,
        header_row=1,
        category="full_container",
        data_mapper=mapper
    )


def search_by_shipping_mark(user_input: str, lang: str) -> dict:
    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        return {
            "shipping_mark": row.get("Shipping mark", "").strip(),
            "name": row.get("Name", "").strip(),
            "product_name": row.get("Product Name", "").strip(),
            "package": row.get("Package", "").strip(),
            "total_cbm": row.get("Total cbm", "").strip(),
            "date_of_arrive": row.get("Date of arrive at destination", "").strip(),
            "status": row.get("Status", "").strip(),
            "destination": row.get("Destination", "").strip(),
        }

    return _process_search(
        user_input=user_input.strip(),
        lang=lang,
        sheet_url=env.CARGO_1_SHEET_URL,
        header_row=2,
        category="groupage_cargo",
        data_mapper=mapper
    )


def search_cargo(cargo_id: str, lang: str) -> dict:
    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        return {
            "id": cargo_id.strip(),
            "client_name": row.get("Client Name", "—").strip(),
            "phone_number": row.get("Telefon Nomer", "—").strip(),
            "product_name": row.get("Product Name", "—").strip(),
            "gross_weight": row.get("GW", "—").strip(),
            "status": row.get("Status", "—").strip()
        }

    return _process_search(
        user_input=cargo_id.strip(),
        lang=lang,
        sheet_url=env.CARGO_2_SHEET_URL,
        header_row=2,
        category="cargo_tracking",
        data_mapper=mapper
    )