from aiogram.types import Message, CallbackQuery
from config import logger
from aiogram import Router, F
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from database import db, accs_action, _tasks
from filters.is_admin import IsAdmin
router = Router()

router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'bot_get_tasks')
async def process_bot_get_tasks(callback: CallbackQuery, state: FSMContext):
    tasks = await _tasks.db_get_all_scheduled_tasks()
    print(tasks)
    if tasks:
        for task in tasks:
            string = ''
            string += (f'\n<b>ID: {task["task_id"]}</b>'
                       f'\n<b>Дата:</b> {task["date"]}'
                       f'\n<b>Аккаунты:</b> {task["accounts"]}'
                       f'\n<b>Сообщение:</b> {task["message"]}'
                       f'\n<b>Задержка (в минутах):</b> {task["timing"]}')
            await callback.message.answer(string, parse_mode='HTML')
    else:
        await callback.message.answer('Нет добавленных рассылок.')


@router.callback_query(F.data == 'bot_get_executed_tasks')
async def process_get_executed_tasks(callback: CallbackQuery):
    tasks = await _tasks.db_get_all_executed_tasks()
    if tasks:
        for task in tasks:
            string = ''
            string += (f'\n<b>ID: {task["task_id"]}</b>'
                       f'\n<b>Дата:</b> {task["date"]}'
                       f'\n<b>Аккаунты:</b> {task["accounts"]}'
                       f'\n<b>Сообщение:</b> {task["message"]}'
                       f'\n<b>Задержка (в минутах):</b> {task["timing"]}')
            await callback.message.answer(string, parse_mode='HTML')
    else:
        await callback.message.answer('Нет выполненных рассылок.')
