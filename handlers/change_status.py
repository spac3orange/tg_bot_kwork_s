from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from keyboards import main_kb
from database import db
from aiogram.fsm.context import FSMContext
from config import logger
from filters.is_admin import IsAdmin
from scheduler import main_scheduler

router = Router()
router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'bot_start')
async def bot_start(callback: CallbackQuery):
    await callback.message.answer('Бот запущен🟢')
    await main_scheduler.toggle_status(True)

@router.callback_query(F.data == 'bot_stop')
async def bot_stop(callback: CallbackQuery):
    await callback.message.answer('Бот выключен🔴')
    await main_scheduler.toggle_status(False)