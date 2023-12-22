from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from keyboards import main_kb
from database import db
from aiogram.fsm.context import FSMContext
from config import logger
from filters.is_admin import IsAdmin
from scheduler import main_scheduler
from pprint import pprint
router = Router()
router.message.filter(
    IsAdmin(F)
)

uistd = []

@router.message(Command(commands='cancel'))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await state.clear()
    scheduler_status = await main_scheduler.get_status()
    scheduler_status = 'Запущен🟢' if scheduler_status else 'Выключен🔴'
    await message.answer('<b>Главное Меню</b>'
                         f'\n\n<b>Статус:</b> {scheduler_status}', reply_markup=main_kb.start_btns(), parse_mode='HTML')

@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    scheduler_status = await main_scheduler.get_status()
    scheduler_status = 'Запущен🟢' if scheduler_status else 'Выключен🔴'
    if uid not in uistd:
        await message.answer_sticker('CAACAgIAAxkBAAJSTWU8mx-ZLZXfU8_ETl0tyrr6s1LtAAJUAANBtVYMarf4xwiNAfowBA')
        await message.answer('<b>Добро пожаловать!</b>'
                             f'\n\n<b>Статус:</b> {scheduler_status}', reply_markup=main_kb.start_btns(), parse_mode='HTML')
        uistd.append(uid)
        pprint(await main_scheduler.get_scheduled_tasks())
    else:
        await message.answer('<b>Главное Меню</b>'
                             f'\n\n<b>Статус:</b> {scheduler_status}', reply_markup=main_kb.start_btns(), parse_mode='HTML')
        pprint(await main_scheduler.get_scheduled_tasks())
        await state.clear()

@router.callback_query(F.data == 'back_to_main_menu')
async def process_back_to_menu(callback: CallbackQuery, state: FSMContext):
    scheduler_status = await main_scheduler.get_status()
    scheduler_status = 'Запущен🟢' if scheduler_status else 'Выключен🔴'
    await callback.message.answer('<b>Главное Меню</b>'
                                  f'\n\n<b>Статус:</b> {scheduler_status}', reply_markup=main_kb.start_btns(), parse_mode='HTML')
    await state.clear()


