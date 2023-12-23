import random
import asyncio
from aiogram.types import Message, CallbackQuery
from config import logger
from aiogram import Router, F
from aiogram.filters import StateFilter
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from config.config_telethon import AuthTelethon
from database import db, accs_action, _tasks
from filters.is_admin import IsAdmin
from states import AddSpamTask
from .spam_settings_menu import process_spam_settings
from scheduler import main_scheduler, process_spam

router = Router()

router.message.filter(
    IsAdmin(F)
)

async def add_scheduler_task(state_data):
    date, accounts, user_message, timing = state_data.values()
    accounts = ','.join(accounts)
    task_id = str(random.randint(1, 9999999))
    task = await main_scheduler.add_task(task_id, process_spam, date, accounts, user_message, int(timing))
    if task:
        await _tasks.db_add_scheduled_task(date, accounts, user_message, task, int(timing), int(task_id))
        return True
    else:
        return False



@router.callback_query(F.data == 'bot_add_task')
async def process_bot_add_task(callback: CallbackQuery, state: FSMContext):
    if not await main_scheduler.get_status():
        await callback.message.answer('Для добавления новых задач, пожалуйста запустите бот.')
        return
    await callback.message.answer('<b>Режим добавления новой рассылки</b>'
                                  '\n\nВведите дату и время рассылки: '
                                  '\nПример: 24/12/2023 12:30'
                                  '\n\nОтменить /cancel', parse_mode='HTML')
    await state.set_state(AddSpamTask.input_date)


@router.message(AddSpamTask.input_date)
async def save_date(message: Message, state: FSMContext):
    if message.text == '/cancel' or message.text == '/start':
        tasks = len(await _tasks.db_get_all_scheduled_tasks())
        executed_tasks = len(await _tasks.db_get_all_executed_tasks())
        await message.answer(f'<b>Запланировано рассылок</b>: {tasks}'
                                      f'\n<b>Выполнено рассылок:</b> {executed_tasks}',
                                      parse_mode='HTML', reply_markup=main_kb.spam_settings())
        await state.clear()
        return
    await state.update_data(date=message.text)
    await message.answer(f'\n<b>Введите номера аккаунтов, с которых будет происходить рассылка:</b>'
                         f'\nПример: 1,2,3,4,5,6,7'
                         f'\nДля добавления всех аккаунтов, введите <b>все</b>'
                         f'\n\nОтменить /cancel', parse_mode='HTML')

    accounts = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in accounts]
    for i, phone in enumerate(phone_list, 1):
        await message.answer(f'{i}. {phone}')
    await state.set_state(AddSpamTask.input_accounts)

@router.message(AddSpamTask.input_accounts)
async def save_accounts(message: Message, state: FSMContext):
    if message.text == '/cancel' or message.text == '/start':
        tasks = len(await _tasks.db_get_all_scheduled_tasks())
        executed_tasks = len(await _tasks.db_get_all_executed_tasks())
        await message.answer(f'<b>Запланировано рассылок</b>: {tasks}'
                                      f'\n<b>Выполнено рассылок:</b> {executed_tasks}',
                                      parse_mode='HTML', reply_markup=main_kb.spam_settings())
        await state.clear()
        return
    all_accs = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in all_accs]
    if message.text == 'все':
        selected_accounts = phone_list
    else:
        indexes = [int(x.strip()) for x in message.text.split(',')]
        selected_accounts = [phone_list[index - 1] for index in indexes if 1 <= index <= len(phone_list)]
    print(selected_accounts)
    await state.update_data(accounts=selected_accounts)
    await message.answer('<b>Введите сообщение для рассылки:</b> '
                         '\n\nОтменить /cancel', parse_mode='HTML')
    await state.set_state(AddSpamTask.input_message)

@router.message(AddSpamTask.input_message)
async def save_message(message: Message, state: FSMContext):
    if message.text == '/cancel' or message.text == '/start':
        tasks = len(await _tasks.db_get_all_scheduled_tasks())
        executed_tasks = len(await _tasks.db_get_all_executed_tasks())
        await message.answer(f'<b>Запланировано рассылок</b>: {tasks}'
                                      f'\n<b>Выполнено рассылок:</b> {executed_tasks}',
                                      parse_mode='HTML', reply_markup=main_kb.spam_settings())
        await state.clear()
        return
    await state.update_data(message=message.text)
    await message.answer('<b>Введите задержку между сообщениями в минутах:</b> '
                         '\nПример: 2'
                         '\n\nОтменить /cancel', parse_mode='HTML')
    await state.set_state(AddSpamTask.input_timing)

@router.message(AddSpamTask.input_timing)
async def save_message(message: Message, state: FSMContext):
    if message.text == '/cancel' or message.text == '/start':
        tasks = len(await _tasks.db_get_all_scheduled_tasks())
        executed_tasks = len(await _tasks.db_get_all_executed_tasks())
        await message.answer(f'<b>Запланировано рассылок</b>: {tasks}'
                                      f'\n<b>Выполнено рассылок:</b> {executed_tasks}',
                                      parse_mode='HTML', reply_markup=main_kb.spam_settings())
        await state.clear()
        return
    await state.update_data(timing=message.text)
    state_data = await state.get_data()
    date, accounts, user_message, timing = state_data.values()
    accounts = '\n'.join(accounts)
    #print(state_data)
    await message.answer(f'<b>Дата:</b> {date}'
                         f'\n<b>Аккаунты:</b> {accounts}'
                         f'\n<b>Сообщение:</b> \n{user_message}'
                         f'\n<b>Задержка между сообщениями:</b> {timing}', parse_mode='HTML', reply_markup=main_kb.task_approve())


@router.callback_query(F.data == 'confirm_task_create')
async def add_task_to_db(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    status = await add_scheduler_task(state_data)
    if status:
        await callback.message.answer('Задача сохранена и добавлена в базу данных.')
    else:
        await callback.message.answer('Ошибка при добавлении задачи. Обратите внимание, что для добавления задачи бот должен быть <b>Запущен</b>')
    await process_spam_settings(callback)
    await state.clear()


@router.callback_query(F.data == 'decline_task_create')
async def add_task_to_db(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Задача отменена.')
    await state.clear()
    await process_spam_settings(callback)