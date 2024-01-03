from aiogram.types import CallbackQuery
from aiogram import Router, F
from keyboards import main_kb
from database import accs_action
from filters.is_admin import IsAdmin
from aiogram.types import FSInputFile
import os

router = Router()
router.message.filter(
    IsAdmin(F)
)
async def get_account_history(phone):
    path = f'history/history_{phone}.txt'
    if os.path.exists(path):
        file = FSInputFile(path)
        return file
    return False

async def get_account_history_errors(phone):
    path = f'history/errors_{phone}.txt'
    if os.path.exists(path):
        file = FSInputFile(path)
        return file
    return False

@router.callback_query(F.data == 'get_history')
async def process_get_history(callback: CallbackQuery):
    operation = 'get_history'
    accs = await accs_action.db_get_all_accounts()
    accs = [acc['phone'] for acc in accs]

    await callback.message.answer('<b>Выберите аккаунт:</b> ', parse_mode='HTML',
                                  reply_markup=main_kb.generate_accs_keyboard(accs, operation, back='back_to_main_menu'))

@router.callback_query(F.data.startswith('account_get_history_'))
async def get_acc_history(callback: CallbackQuery):
    phone = callback.data.split('_')[-1]
    file = await get_account_history(phone)
    file_errors = await get_account_history_errors(phone)
    if not file and not file_errors:
        await callback.message.answer(f'История аккаунта <b>{phone}</b> не найдена.', parse_mode='HTML')
    if file:
        await callback.message.answer_document(document=file, caption=f'История аккаунта {phone}')
    if file_errors:
        await callback.message.answer_document(document=file_errors, caption=f'Ошибки аккаунта {phone}')
