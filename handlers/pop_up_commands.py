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


@router.message(Command('bot_status'))
async def process_bot_status(message: Message):
    bot_status = await main_scheduler.get_status()
    bot_status = 'Работает🟢' if bot_status else 'Выключен🔴'
    await message.answer(bot_status)