from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from database import db, accs_action
from filters.is_admin import IsAdmin
router = Router()

router.message.filter(
    IsAdmin(F)
)

@router.callback_query(F.data == 'tg_accounts')
async def process_accounts_menu(callback: CallbackQuery, state: FSMContext):
    accounts = await accs_action.db_get_all_accounts()
    phones = [acc['phone'] for acc in accounts]
    sent_msg = [acc['comments_sent'] for acc in accounts]
    acc_string = ''
    for phone, msg in zip(phones, sent_msg):
        acc_string += f'\n\n<b>Аккаунт:</b> {phone} \n<b>Отправлено сообщений:</b> {msg}'

    banned_accounts = await accs_action.get_banned_phones()
    await callback.message.answer(f'<b>Активные аккаунты:</b> {len(accounts)}'
                                  f'{acc_string}'
                                  f'\n\n<b>Забаненные аккаунты:</b> {len(banned_accounts)}'
                                  '\n\n<b>Настройки Telegram аккаунтов</b>: ', parse_mode='HTML', reply_markup=main_kb.accs_settings_menu())
    await state.clear()
