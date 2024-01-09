import random
from config import logger
from config import TelethonConnect
from database import _tasks
from scheduler import main_scheduler
from utils import inform_admins
import asyncio


async def process_spam(accounts, user_message, timing, task_id):
    try:
        accounts = accounts.split(',')
        accounts = [x.strip() for x in accounts]
        await inform_admins(f'Начинаю выполнение задачи {task_id}...')
        for acc in accounts:
            try:
                session = TelethonConnect(acc)
                task = asyncio.create_task(session.spam_groups(user_message, timing))
                await asyncio.sleep(random.randint(0, 10))
            except Exception as e:
                logger.error(e)
                pass
    except Exception as e:
        logger.error(e)
        pass
    finally:
        await asyncio.sleep(60)
        await inform_admins(f'Задача {task_id} выполнена.')
        task = asyncio.create_task(_tasks.db_execute_scheduled_task(int(task_id)))

