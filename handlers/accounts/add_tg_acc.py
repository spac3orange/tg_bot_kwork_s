import random
import asyncio
from aiogram.types import Message, CallbackQuery
from config import logger
from aiogram import Router, F
from aiogram.filters import StateFilter
from keyboards import main_kb
from aiogram.fsm.context import FSMContext
from config.config_telethon import AuthTelethon
from database import db, accs_action
from telethon import errors
from filters.is_admin import IsAdmin
from states import AddTgAccState
router = Router()

router.message.filter(
    IsAdmin(F)
)

async def acc_in_table(phone):
    accounts = await accs_action.db_get_all_accounts()
    for a in accounts:
        print(a)
        if phone in a:
            return True
        return False


@router.callback_query(F.data == 'tg_accs_add')
async def input_proxy(callback: CallbackQuery, state: FSMContext):
    logger.info('awaiting phone to add telegram account')
    await callback.message.answer("Пожалуйста, введите прокси <b>SOCKS5</b> в следующем формате:\n"
                                  "customer-dedu:qux40tn81pt17qmcU@ru-pr.oxylabs.io:40000\n\n"
                                  "Где:\n"
                                  "- <b>'customer-dedu'</b> - это имя пользователя\n"
                                  "- <b>'qux40tn81pt17qmcU'</b> - это пароль\n"
                                  "- <b>'ru-pr.oxylabs.io'</b> - это хост\n"
                                  "- <b>'40000'</b> - это порт"
                                  "\n\nЕсли аккаунт будет работать без прокси, введите <b>нет</b>"
                                  "\n\nОтменить /cancel", parse_mode='HTML')

    await state.set_state(AddTgAccState.input_proxy)

@router.message(AddTgAccState.input_proxy)
async def input_phone(message: Message, state: FSMContext):
    if message.text == '/cancel':
        accounts = await accs_action.db_get_all_accounts()
        banned_accounts = await accs_action.get_banned_phones()
        phones = [acc['phone'] for acc in accounts]
        sent_msg = [acc['comments_sent'] for acc in accounts]
        acc_string = ''
        for phone, msg in zip(phones, sent_msg):
            acc_string += f'\n\n<b>Аккаунт:</b> {phone} \n<b>Отправлено сообщений:</b> {msg}'

        await message.answer(f'<b>Активные аккаунты:</b> {len(accounts)}'
                                      f'{acc_string}'
                                      f'\n\n<b>Забаненные аккаунты:</b> {len(banned_accounts)}'
                                      '\n\n<b>Настройки Telegram аккаунтов</b>: ', parse_mode='HTML', reply_markup=main_kb.accs_settings_menu())
        await state.clear()
        return

    await state.update_data(proxy=message.text)
    logger.info('awaiting phone to add telegram account')
    await message.answer('Пожалуйста, введите номер телефона: '
                                  '\n\nОтменить /cancel')
    await state.set_state(AddTgAccState.input_2fa)


@router.message(AddTgAccState.input_2fa)
async def input_2fa(message: Message, state: FSMContext):
    if message.text == '/cancel':
        accounts = await accs_action.db_get_all_accounts()
        banned_accounts = await accs_action.get_banned_phones()
        phones = [acc['phone'] for acc in accounts]
        sent_msg = [acc['comments_sent'] for acc in accounts]
        acc_string = ''
        for phone, msg in zip(phones, sent_msg):
            acc_string += f'\n\n<b>Аккаунт:</b> {phone} \n<b>Отправлено сообщений:</b> {msg}'

        await message.answer(f'<b>Активные аккаунты:</b> {len(accounts)}'
                             f'{acc_string}'
                             f'\n\n<b>Забаненные аккаунты:</b> {len(banned_accounts)}'
                             '\n\n<b>Настройки Telegram аккаунтов</b>: ', parse_mode='HTML', reply_markup=main_kb.accs_settings_menu())
        await state.clear()
        return

    await message.answer('Введите пароль 2fa:\n'
                         'Если пароль не установлен, введите "нет"'
                         '\n\nОтменить /cancel')
    await state.update_data(phone=message.text)
    await state.set_state(AddTgAccState.input_number)


@router.message(AddTgAccState.input_number)
async def input_code(message: Message, state: FSMContext):
    if message.text == '/cancel':
        accounts = await accs_action.db_get_all_accounts()
        banned_accounts = await accs_action.get_banned_phones()
        phones = [acc['phone'] for acc in accounts]
        sent_msg = [acc['comments_sent'] for acc in accounts]
        acc_string = ''
        for phone, msg in zip(phones, sent_msg):
            acc_string += f'\n\n<b>Аккаунт:</b> {phone} \n<b>Отправлено сообщений:</b> {msg}'

        await message.answer(f'<b>Активные аккаунты:</b> {len(accounts)}'
                             f'{acc_string}'
                             f'\n\n<b>Забаненные аккаунты:</b> {len(banned_accounts)}'
                             '\n\n<b>Настройки Telegram аккаунтов</b>: ', parse_mode='HTML', reply_markup=main_kb.accs_settings_menu())
        await state.clear()
        return

    await state.update_data(password=message.text)

    data = await state.get_data()
    phone = data['phone']
    proxy = data['proxy']
    print(phone)
    if not await acc_in_table(phone):
        logger.info('awaiting for auth code in telegram')
        await message.answer('Запрашиваю код подтверждения...')
        if proxy == 'нет':
            auth = AuthTelethon(phone)
        else:
            auth = AuthTelethon(phone, proxy)

        await state.update_data(tg_client=auth)
        if await auth.login_phone():
            await message.answer('Код подтверждения отправлен.\n'
                                 'Пожалуйста, проверьте телеграм и введите код:')
        else:
            await message.answer('Ошибка при попытке отправить код подтверждения.'
                                 '\nПожалуйста, попробуйте еще раз.')
            await message.answer('<b>Настройки Telegram аккаунтов</b>: ', parse_mode='HTML', reply_markup=main_kb.accs_settings_menu())
            await state.clear()
        await state.set_state(AddTgAccState.input_code)
    else:
        logger.error(f'account with phone {phone} already exists in db')
        await message.answer(f'Аккаунт с номером {phone} уже существует в базе данных.')
        await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=main_kb.accs_settings_menu())


@router.message(StateFilter(AddTgAccState.input_code))
async def add_tg_acc(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        print(data)
        password = data['password']
        print(password)
        await data['tg_client'].login_process_code(message.text)
        await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
        await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=main_kb.accs_settings_menu())
        asyncio.create_task(accs_action.db_add_tg_account(data['phone']))
        logger.info('telegram account successfully added to db')

    except errors.SessionPasswordNeededError as e:
        try:
            logger.error(e)
            await data['tg_client'].login_process_code(password=password)
            await message.answer('Аккаунт успешно подключен и добавлен в базу данных.')
            await message.answer(f'Настройки телеграм аккаунтов:', reply_markup=main_kb.accs_settings_menu())
            asyncio.create_task(accs_action.db_add_tg_account(data['phone']))
            logger.info('telegram account successfully added to db')
        except Exception as e:
            logger.error(e)
            await message.answer('Ошибка логина. Пожалуйста, попробуйте еще раз.')
            return

    await state.clear()
