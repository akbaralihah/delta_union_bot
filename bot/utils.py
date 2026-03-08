import html
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Callable, Any

import gspread_asyncio
from google.oauth2.service_account import Credentials
from gspread.exceptions import GSpreadException
from cachetools import TTLCache
from redis.asyncio import Redis

from bot.translations import translate
from settings import settings

logger = logging.getLogger(__name__)


def get_creds() -> Credentials:
    creds = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH)
    scoped_creds = creds.with_scopes([
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ])
    return scoped_creds


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)

redis_cache = Redis.from_url(settings.redis_url, decode_responses=True)


class AsyncGoogleSheetsManager:
    def __init__(self, client_manager: gspread_asyncio.AsyncioGspreadClientManager, redis: Redis):
        self.client_manager = client_manager
        self.cache = redis

    async def get_all_records(self, url: str) -> list[dict]:
        cached_data = await self.cache.get(url)
        if cached_data:
            return json.loads(cached_data)

        try:
            client = await self.client_manager.authorize()
            spreadsheet = await client.open_by_url(url)
            sheet = await spreadsheet.get_worksheet(0)
            records = await sheet.get_all_records()

            await self.cache.setex(url, 60, json.dumps(records))
            return records

        except Exception as e:
            logger.error(f"Google Sheets fetch error for {url}: {e}")
            return []

    async def get_sheet(self, url: str) -> Optional[gspread_asyncio.AsyncioGspreadWorksheet]:
        try:
            client = await self.client_manager.authorize()
            spreadsheet = await client.open_by_url(url)
            return await spreadsheet.get_worksheet(0)
        except Exception as e:
            logger.error(f"Cannot connect to table {url}: {e}")
            return None

    async def find_row_by_value(
            self,
            sheet: Optional[gspread_asyncio.AsyncioGspreadWorksheet],
            search_value: str,
            header_row: int = 1
    ) -> Optional[Dict[str, str]]:
        if not sheet:
            return None

        try:
            cell = await sheet.find(search_value)
            if not cell or cell.row <= header_row:
                return None

            headers = await sheet.row_values(header_row)
            row_data = await sheet.row_values(cell.row)

            return {headers[i]: (row_data[i] if i < len(row_data) else "") for i in range(len(headers))}

        except GSpreadException as e:
            logger.error(f"GSpread search error: {e}")
            raise


gs_manager = AsyncGoogleSheetsManager(agcm, redis_cache)


def _build_response(status: int, message: str) -> Dict[str, Any]:
    # Use the first admin from settings as a fallback for reception
    reception = settings.ADMINS[0] if settings.ADMINS else 0
    return {"status": status, "message": message, "reception": reception}


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


async def _process_search(
        user_input: str,
        lang: str,
        sheet_url: str,
        header_row: int,
        category: str,
        data_mapper: Callable[[Dict[str, str]], Dict[str, str]]
) -> Dict[str, Any]:
    if not user_input:
        return _build_response(400, "Input not entered.")

    sheet = await gs_manager.get_sheet(sheet_url)
    if not sheet:
        return _build_response(500, "Error: Unable to connect to Google Sheets.")

    try:
        row = await gs_manager.find_row_by_value(sheet, user_input, header_row=header_row)
    except GSpreadException as e:
        return _build_response(400, f"Error retrieving data: {e}")

    if not row:
        return _build_response(404, "Data not found.")

    data = data_mapper(row)
    reply_message = _generate_html_reply(data, lang, category)
    return _build_response(200, reply_message)


async def track(user_input: str, lang: str) -> Dict[str, Any]:
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

    return await _process_search(
        user_input=clean_input,
        lang=lang,
        sheet_url=settings.CONTAINER_SHEET_URL,
        header_row=1,
        category="full_container",
        data_mapper=mapper
    )


async def search_by_shipping_mark(user_input: str, lang: str) -> Dict[str, Any]:
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

    return await _process_search(
        user_input=user_input.strip(),
        lang=lang,
        sheet_url=settings.CARGO_1_SHEET_URL,
        header_row=2,
        category="groupage_cargo",
        data_mapper=mapper
    )


async def search_cargo(cargo_id: str, lang: str) -> Dict[str, Any]:
    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        return {
            "id": cargo_id.strip(),
            "client_name": row.get("Client Name", "—").strip(),
            "phone_number": row.get("Telefon Nomer", "—").strip(),
            "product_name": row.get("Product Name", "—").strip(),
            "gross_weight": row.get("GW", "—").strip(),
            "status": row.get("Status", "—").strip()
        }

    return await _process_search(
        user_input=cargo_id.strip(),
        lang=lang,
        sheet_url=settings.CARGO_2_SHEET_URL,
        header_row=2,
        category="cargo_tracking",
        data_mapper=mapper
    )
