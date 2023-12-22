from aiogram.types import CallbackQuery
from aiogram import Router, F
from keyboards import main_kb
from config import logger
from aiogram.fsm.context import FSMContext
from filters.is_admin import IsAdmin
from states import DelTgAccState
from database import db, accs_action
router = Router()

router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'tg_accs_del')
async def del_input_phone(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to delete telegram account')
    tg_accs = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in tg_accs]

    await callback.message.answer('Пожалуйста, выберите номер телефона удаляемого аккаунта: ',
                                  reply_markup=main_kb.generate_accs_keyboard(phone_list, 'delete', back='tg_accounts'))
    await state.set_state(DelTgAccState.input_number)


@router.callback_query(F.data.startswith('account_delete'))
async def acc_deleted(callback: CallbackQuery, state: FSMContext):
    acc = callback.data.split('_')[-1]
    await accs_action.db_delete_account(acc)
    logger.info('telegram account deleted from db')
    await callback.message.answer('Аккаунт удален из базы данных')
    await callback.message.answer('Настройки телеграм аккаунтов:', reply_markup=main_kb.accs_settings_menu())
    await state.clear()
