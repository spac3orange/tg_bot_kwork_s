import asyncio

from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from database import db, accs_action, _proxy
from filters.is_admin import IsAdmin
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from states import SetProxy, CheckProxy
from utils import check_proxy
router = Router()

router.message.filter(
    IsAdmin(F)
)


@router.callback_query(F.data == 'tg_accs_proxy')
async def process_add_proxy(callback: CallbackQuery):
    tg_accs = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in tg_accs]
    proxy_list = [acc['proxy'] for acc in tg_accs]
    message = ''
    for phone, proxy in zip(phone_list, proxy_list):
        proxy = 'Не установлен' if not proxy else proxy
        message += f'<b>Аккаунт</b>: {phone}' \
                   f'\n<b>Прокси:</b> {proxy}'
        await callback.message.answer(message, parse_mode='HTML')
        message = ''
    await callback.message.answer('<b>Настройки прокси:</b>', reply_markup=main_kb.proxy_settings_menu(), parse_mode='HTML')


@router.callback_query(F.data == 'change_proxy')
async def change_proxy(callback: CallbackQuery):
    tg_accs = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in tg_accs]
    operation = 'chproxy'
    await callback.message.answer('<b>Выберите аккаунт: </b>', parse_mode='HTML',
                                  reply_markup=main_kb.generate_accs_keyboard(phone_list, operation, back='tg_accs_proxy'))


@router.callback_query(F.data.startswith('account_chproxy_'))
async def process_acc_change_proxy(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SetProxy.input_proxy)
    print(callback.data)
    account = callback.data.split('_')[-1]
    await state.update_data(account=account)
    await callback.message.answer(f'<b>Выбран аккаунт</b>: {account}', parse_mode='HTML')
    await callback.message.answer("Пожалуйста, введите прокси <b>SOCKS5</b> в следующем формате:\n"
                                  "customer-dedu:qux40tn81pt17qmcU@ru-pr.oxylabs.io:40000\n\n"
                                  "Где:\n"
                                  "- <b>'customer-dedu'</b> - это имя пользователя\n"
                                  "- <b>'qux40tn81pt17qmcU'</b> - это пароль\n"
                                  "- <b>'ru-pr.oxylabs.io'</b> - это хост\n"
                                  "- <b>'40000'</b> - это порт"
                                  "\n\nОтменить /cancel", parse_mode='HTML')

@router.message(SetProxy.input_proxy)
async def update_acc_proxy(message: Message, state: FSMContext):
    proxy = message.text
    tg_accs = await accs_action.db_get_all_accounts()

    if message.text == '/cancel' or message.text == '/start':
        phone_list = [acc['phone'] for acc in tg_accs]
        operation = 'chproxy'
        await message.answer('<b>Выберите аккаунт: </b>', parse_mode='HTML',
                             reply_markup=main_kb.generate_accs_keyboard(phone_list, operation, back='tg_accs_proxy'))
        await state.clear()
        return
    #test proxy here
    await state.update_data(proxy=proxy)
    state_data = await state.get_data()
    await _proxy.update_proxy_for_phone(state_data['account'], state_data['proxy'])
    await message.answer('Прокси обновлен.')
    await state.clear()

    await asyncio.sleep(1)
    phone_list = [acc['phone'] for acc in tg_accs]
    operation = 'chproxy'
    await message.answer('<b>Выберите аккаунт: </b>', parse_mode='HTML',
                         reply_markup=main_kb.generate_accs_keyboard(phone_list, operation, back='tg_accs_proxy'))


@router.callback_query(F.data == 'check_proxy')
async def process_check_proxy(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, введите прокси <b>SOCKS5</b> в следующем формате:\n"
                                  "customer-dedu:qux40tn81pt17qmcU@ru-pr.oxylabs.io:40000\n\n"
                                  "Где:\n"
                                  "- <b>'customer-dedu'</b> - это имя пользователя\n"
                                  "- <b>'qux40tn81pt17qmcU'</b> - это пароль\n"
                                  "- <b>'ru-pr.oxylabs.io'</b> - это хост\n"
                                  "- <b>'40000'</b> - это порт"
                                  "\n\nОтменить /cancel", parse_mode='HTML')
    await state.set_state(CheckProxy.input_proxy)

@router.message(CheckProxy.input_proxy)
async def process_check_proxy(message: Message, state: FSMContext):
    proxy = message.text
    print(proxy)
    try:
        if proxy == '/cancel' or proxy == '/start':
            tg_accs = await accs_action.db_get_all_accounts()
            phone_list = [acc['phone'] for acc in tg_accs]
            proxy_list = [acc['proxy'] for acc in tg_accs]
            mess = ''
            for phone, proxy in zip(phone_list, proxy_list):
                proxy = 'Не установлен' if not proxy else proxy
                mess += f'<b>Аккаунт</b>: {phone}' \
                           f'\n<b>Прокси:</b> {proxy}'
                await message.answer(mess, parse_mode='HTML')
                mess = ''
            await message.answer('<b>Настройки прокси:</b>', reply_markup=main_kb.proxy_settings_menu(), parse_mode='HTML')
            await state.clear()
            return

        else:
            proxy_status = await check_proxy(proxy)
            proxy_status = 'Прокси работает' if proxy_status else 'Прокси не работает'
            await message.answer(proxy_status)

            tg_accs = await accs_action.db_get_all_accounts()
            phone_list = [acc['phone'] for acc in tg_accs]
            proxy_list = [acc['proxy'] for acc in tg_accs]
            mess = ''
            for phone, proxy in zip(phone_list, proxy_list):
                proxy = 'Не установлен' if not proxy else proxy
                mess += f'<b>Аккаунт</b>: {phone}' \
                           f'\n<b>Прокси:</b> {proxy}'
                await message.answer(mess, parse_mode='HTML')
                mess = ''
            await message.answer('<b>Настройки прокси:</b>', reply_markup=main_kb.proxy_settings_menu(), parse_mode='HTML')
            await state.clear()
            return
    except Exception as e:
        print(e)
        await state.clear()

