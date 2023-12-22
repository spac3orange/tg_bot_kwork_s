import random
import asyncio
from aiogram.types import Message, CallbackQuery
from config import logger
from aiogram import Router, F
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from database import db, accs_action, _tasks
from filters.is_admin import IsAdmin
from .spam_settings_menu import process_spam_settings
from scheduler import main_scheduler
router = Router()

router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'bot_del_task')
async def process_bot_del_task(callback: CallbackQuery, state: FSMContext):
    tasks = await _tasks.db_get_all_scheduled_tasks()
    tasks_ids = [task['task_id'] for task in tasks]
    print(tasks_ids)
    operation = 'del_task'
    print(tasks)
    await callback.message.answer('<b>Активные задачи:</b>', parse_mode='HTML')
    for i, task in enumerate(tasks, 1):
        string = ''
        string += (f'\n<b>ID: {task["task_id"]}</b>'
                   f'\n<b>Дата:</b> {task["date"]}'
                   f'\n<b>Аккаунты:</b> {task["accounts"]}'
                   f'\n<b>Сообщение:</b> {task["message"]}'
                   f'\n<b>Задержка (в минутах):</b> {task["timing"]}')
        await callback.message.answer(string, parse_mode='HTML')
    await callback.message.answer('<b>Выберите id задач, которые будут удалены:</b> ',
                                  parse_mode='HTML', reply_markup=main_kb.generate_tasks_keyboard(tasks_ids, operation))


@router.callback_query(F.data.startswith('task_del_task_'))
async def process_task_deleted(callback: CallbackQuery):
    task_id = int(callback.data.split('_')[-1])
    if await main_scheduler.get_status():
        await main_scheduler.remove_task(task_id)
    await _tasks.delete_scheduled_task(task_id)

    await callback.message.answer(f'Задача <b>{task_id}</b> удалена.', parse_mode='HTML')
    await process_spam_settings(callback)
