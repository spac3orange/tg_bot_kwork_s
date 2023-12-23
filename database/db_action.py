import asyncpg
from environs import Env
from config import logger
from typing import List, Dict, Tuple
import asyncio

class Database:
    def __init__(self):
        self.env = Env()
        self.env.read_env(path='config/.env')
        self.user = self.env.str('DB_USER')
        self.password = self.env.str('DB_PASSWORD')
        self.host = self.env.str('DB_HOST')
        self.db_name = self.env.str('DB_NAME')
        self.db_port = self.env.str('DB_PORT')
        self.pool = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=self.user,
                password=self.password,
                host=self.host,
                database=self.db_name,
                port=self.db_port,
                max_size=50,
            )

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while creating connection pool", error)
            print(error)

    async def close_pool(self):
        if self.pool:
            await self.pool.close()

    async def execute_query(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while executing query", error)

    async def fetch_row(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            print("Error while fetching row", error)

    async def fetch_all(self, query, *args):
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while fetching all", error)

    async def db_start(self) -> None:
        """
        Initializes the connection to the database and creates the tables if they do not exist.
        """
        try:

            await self.create_pool()
            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS telegram_accounts (
                    phone TEXT PRIMARY KEY,
                    comments_sent INTEGER DEFAULT 0,
                    proxy TEXT DEFAULT 'no',
                    status TEXT DEFAULT 'Active'
                )
            """)

            await self.execute_query("""
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    date TEXT,
                    accounts TEXT,
                    message TEXT,
                    scheduler_object BYTEA PRIMARY KEY,
                    timing INTEGER,
                    task_id BIGINT
                )
            """)

            await self.execute_query("""
                            CREATE TABLE IF NOT EXISTS executed_tasks (
                                date TEXT,
                                accounts TEXT,
                                message TEXT,
                                scheduler_object BYTEA PRIMARY KEY,
                                timing INTEGER,
                                task_id BIGINT
                            )
                        """)

            logger.info('connected to database')

        except (Exception, asyncpg.PostgresError) as error:
            logger.error("Error while connecting to DB", error)


db = Database()