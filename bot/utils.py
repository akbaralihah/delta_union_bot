import html
import json
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Callable, Any

import gspread_asyncio
from google.oauth2.service_account import Credentials
from redis.asyncio import Redis

from bot.translations import translate
from db.configs import redis_client
from settings import settings

logger = logging.getLogger(__name__)


def get_creds() -> Credentials:
    creds = Credentials.from_service_account_file(settings.GOOGLE_CREDENTIALS_PATH)
    scoped_creds = creds.with_scopes(
        [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
    )
    return scoped_creds


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


class AsyncGoogleSheetsManager:
    def __init__(
        self, client_manager: gspread_asyncio.AsyncioGspreadClientManager, redis: Redis
    ):
        self.client_manager = client_manager
        self.cache = redis

    async def update_cache(self, url: str, header_row: int = 1) -> None:
        """Скачивает данные из таблицы и обновляет кэш Redis."""
        cache_key = f"sheet:{url}:head:{header_row}"
        try:
            self.client_manager.client = None
            client = await self.client_manager.authorize()
            spreadsheet = await client.open_by_url(url)
            sheet = await spreadsheet.get_worksheet(0)

            values = await sheet.get_all_values()

            if len(values) < header_row:
                return

            raw_headers = values[header_row - 1]
            unique_headers = []
            for i, h in enumerate(raw_headers):
                h_str = str(h).strip()
                if not h_str or h_str in unique_headers:
                    unique_headers.append(f"{h_str}_{i}" if h_str else f"Col_{i}")
                else:
                    unique_headers.append(h_str)

            records = [dict(zip(unique_headers, row)) for row in values[header_row:]]

            # Сохраняем в кэш на 2 часа (7200 секунд), чтобы данные жили до следующего успешного обновления
            await self.cache.setex(cache_key, 7200, json.dumps(records))
            logger.info(f"✅ Cache updated successfully for {url}")

        except Exception as e:
            logger.error(f"❌ Google Sheets fetch error for {url}: {e}")

    async def get_all_records(self, url: str, header_row: int = 1) -> list[dict]:
        """Мгновенно получает данные только из кэша Redis."""
        cache_key = f"sheet:{url}:head:{header_row}"
        cached_data = await self.cache.get(cache_key)

        if cached_data:
            return json.loads(cached_data)

        # Если данных в Redis еще нет (например, при самом первом запуске)
        return []


gs_manager = AsyncGoogleSheetsManager(agcm, redis_client)


# --- Фоновая задача синхронизации ---
async def periodic_sheets_sync():
    """Фоновый процесс: обновляет данные каждые 30 минут."""
    # Даем боту пару секунд на инициализацию перед первым запуском
    await asyncio.sleep(2)
    while True:
        logger.info("🔄 Starting periodic sync of Google Sheets...")
        await gs_manager.update_cache(settings.CONTAINER_SHEET_URL, header_row=1)
        await gs_manager.update_cache(settings.CARGO_1_SHEET_URL, header_row=2)
        await gs_manager.update_cache(settings.CARGO_2_SHEET_URL, header_row=2)
        logger.info("⏳ Periodic sync completed. Waiting 30 minutes.")

        # Спим 30 минут (1800 секунд)
        await asyncio.sleep(1800)


def _build_response(status: int, message: str) -> Dict[str, Any]:
    return {"status": status, "message": message, "reception": settings.ERROR_GROUP_ID}


def _generate_html_reply(data: Dict[str, str], lang: str, category: str) -> str:
    reply = f"<b>{translate(lang, 'message.header')}</b>\n\n"
    for key, value in data.items():
        if not value or value == "—":
            continue
        label = translate(lang, f"message.{category}.{key}")
        reply += (
            f"<b>{html.escape(label)}:</b> <code>{html.escape(str(value))}</code>\n"
        )

    reply += f"<b>{translate(lang, 'message.date')}:</b> <code>{datetime.now().strftime('%d-%m-%Y')}</code>\n\n"
    reply += f"<b>{translate(lang, 'message.footer')}</b>"
    return reply


async def _process_search(
    user_input: str,
    lang: str,
    sheet_url: str,
    header_row: int,
    category: str,
    data_mapper: Callable[[Dict[str, str]], Dict[str, str]],
) -> Dict[str, Any]:
    if not user_input:
        return _build_response(400, "Input not entered.")

    records = await gs_manager.get_all_records(sheet_url, header_row)

    if not records:
        return _build_response(
            503, "⏳ Данные загружаются, пожалуйста, попробуйте через минуту."
        )

    user_input_lower = user_input.lower().strip()
    found_row = None

    for row in records:
        if any(user_input_lower in str(val).lower().strip() for val in row.values()):
            found_row = row
            break

    if not found_row:
        return _build_response(404, translate(lang, "message.waiting_for_data"))

    try:
        data = data_mapper(found_row)
        reply_message = _generate_html_reply(data, lang, category)
        return _build_response(200, reply_message)
    except Exception as e:
        logger.error(f"Data mapping error: {e}")
        return _build_response(500, "Error formatting data.")


# --- Функции поиска (теперь без таймаутов, так как Redis быстрый) ---
async def track(user_input: str, lang: str) -> Dict[str, Any]:
    clean_input = user_input.replace("#", "").strip()

    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        status = row.get("Customer status")
        if not status:
            status = translate(lang, "message.waiting_for_data")
        if str(status).isdigit():
            status = str(status) + "km"

        return {
            "product_name": str(row.get("Product name", "")).strip(),
            "container_id": str(row.get("Container №", ""))
            .replace("#", "")
            .strip()
            .upper(),
            "platform_id": str(
                row.get("KZ Platform", "") or row.get("ChN Platform", "")
            ).strip(),
            "status": str(status).strip(),
        }

    return await _process_search(
        user_input=clean_input,
        lang=lang,
        sheet_url=settings.CONTAINER_SHEET_URL,
        header_row=1,
        category="full_container",
        data_mapper=mapper,
    )


async def search_by_shipping_mark(user_input: str, lang: str) -> Dict[str, Any]:
    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        return {
            "shipping_mark": str(row.get("Shipping mark", "")).strip(),
            "name": str(row.get("Name", "")).strip(),
            "product_name": str(row.get("Product Name", "")).strip(),
            "package": str(row.get("Package", "")).strip(),
            "total_cbm": str(row.get("Total cbm", "")).strip(),
            "date_of_arrive": str(row.get("Date of arrive at destination", "")).strip(),
            "status": str(row.get("Status", "")).strip(),
            "destination": str(row.get("Destination", "")).strip(),
        }

    return await _process_search(
        user_input=user_input.strip(),
        lang=lang,
        sheet_url=settings.CARGO_1_SHEET_URL,
        header_row=2,
        category="groupage_cargo",
        data_mapper=mapper,
    )


async def search_cargo(cargo_id: str, lang: str) -> Dict[str, Any]:
    def mapper(row: Dict[str, str]) -> Dict[str, str]:
        return {
            "id": str(cargo_id).strip(),
            "client_name": str(row.get("Client Name", "—")).strip(),
            "phone_number": str(row.get("Telefon Nomer", "—")).strip(),
            "product_name": str(row.get("Product Name", "—")).strip(),
            "gross_weight": str(row.get("GW", "—")).strip(),
            "status": str(row.get("Status", "—")).strip(),
        }

    return await _process_search(
        user_input=cargo_id.strip(),
        lang=lang,
        sheet_url=settings.CARGO_2_SHEET_URL,
        header_row=2,
        category="cargo_tracking",
        data_mapper=mapper,
    )
