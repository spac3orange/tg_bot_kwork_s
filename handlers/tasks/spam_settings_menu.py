from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import main_kb
from filters.is_admin import IsAdmin
from database import _tasks
router = Router()

router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'spam_settings')
async def process_spam_settings(callback: CallbackQuery):
    tasks = len(await _tasks.db_get_all_scheduled_tasks())
    executed_tasks = len(await _tasks.db_get_all_executed_tasks())
    await callback.message.answer(f'<b>Запланировано рассылок</b>: {tasks}'
                                  f'\n<b>Выполнено рассылок:</b> {executed_tasks}',
                                  parse_mode='HTML', reply_markup=main_kb.spam_settings())