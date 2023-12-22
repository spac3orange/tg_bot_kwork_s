from config import TelethonConnect
from database import _tasks
from scheduler import main_scheduler
from utils import inform_admins
import asyncio


async def process_spam(accounts, user_message, timing, task_id):
    accounts = accounts.split(',')
    accounts = [x.strip() for x in accounts]
    await inform_admins(f'Начинаю выполнение задачи {task_id}...')
    for acc in accounts:
        session = TelethonConnect(acc)
        asyncio.create_task(session.spam_groups(user_message, timing))
    await asyncio.sleep(60)
    await _tasks.db_execute_scheduled_task(int(task_id))
    await inform_admins(f'Задача {task_id} выполнена.')

