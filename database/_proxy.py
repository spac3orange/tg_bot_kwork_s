from . import db
import asyncpg
from config import logger


async def update_proxy_for_phone(phone: str, proxy: str):
    try:
        query = "UPDATE telegram_accounts SET proxy = $1 WHERE phone = $2"
        await db.execute_query(query, proxy, phone)
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error updating proxy for phone {phone}: {error}")