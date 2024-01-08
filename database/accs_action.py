from . import db
import asyncpg
from config import logger
from typing import List

async def db_add_tg_account(phone_number: str) -> None:
    """
    Adds a Telegram account to the database.
    """
    try:

        query = "INSERT INTO telegram_accounts(phone) VALUES ($1)"
        await db.execute_query(query, phone_number)
        logger.info(f"Telegram account {phone_number} added to the database")

    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error adding Telegram account to the database: {error}")


async def db_get_all_accounts():
    try:
        query = "SELECT * FROM telegram_accounts WHERE status = 'Active'"
        results = await db.fetch_all(query)
        accounts = []
        for row in results:
            account = {
                'phone': row['phone'],
                'comments_sent': row['comments_sent'],
                'proxy': row['proxy'],
                'status': row['status']
            }
            accounts.append(account)
        return accounts
    except Exception as error:
        print("Error while getting all accounts", error)
        return []


async def db_delete_account(phone_number: str) -> None:
    try:
        query = "DELETE FROM telegram_accounts WHERE phone = $1"
        await db.execute_query(query, phone_number)
        logger.info(f"Telegram account {phone_number} deleted from the database")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error deleting Telegram account from the database: {error}")


async def get_banned_phones() -> List[str]:
    try:
        query = "SELECT phone FROM telegram_accounts WHERE status = 'Banned'"
        rows = await db.fetch_all(query)
        phones = [row['phone'] for row in rows]
        return phones
    except (Exception, asyncpg.PostgresError) as error:
        logger.error("Error while retrieving banned phones from telegram_accounts table", error)
        return []


async def db_add_banned_account(phone_number: str) -> None:
    try:
        query = "UPDATE telegram_accounts SET status = 'Banned' WHERE phone = $1"
        await db.execute_query(query, phone_number)
        logger.info(f"Status of Telegram account {phone_number} updated to 'Banned'")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error updating status of Telegram account in the database: {error}")


async def db_increment_comments_sent(phone_number: str) -> None:
    try:
        query = "SELECT comments_sent FROM telegram_accounts WHERE phone = $1 FOR UPDATE"
        result = await db.fetch_row(query, phone_number)
        comments_sent = result['comments_sent'] + 1
        query = "UPDATE telegram_accounts SET comments_sent = $1 WHERE phone = $2"
        await db.execute_query(query, comments_sent, phone_number)
        logger.info(f"Value of comments_sent for Telegram account {phone_number} incremented by 1")
    except (Exception, asyncpg.PostgresError) as error:
        logger.error(f"Error incrementing comments_sent for Telegram account in the database: {error}")