import asyncio
import random
from keyboards import main_kb
from aiogram.types import CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from config.config_telethon import TelethonConnect
from database import db, accs_action
from typing import List, Tuple
from filters import IsAdmin
router = Router()

router.message.filter(
    IsAdmin(F)
)



async def get_info(accounts: list, uid) -> List[Tuple[str]]:
    accs_info = []
    for session in accounts:
        try:
            slp = random.randint(0, 5)
            await asyncio.sleep(slp)
            sess = TelethonConnect(session)
            acc_info = await sess.get_info()
            if acc_info:
                accs_info.append(acc_info)
            else:
                await aiogram_bot.send_message(uid, text=f'Ошибка. Аккаунт <b>{session}</b> не авторизован. ', parse_mode='HTML')
                continue
        except Exception as e:
            print(e)
    #print(f'accs_info = {accs_info}')
    return accs_info

@router.callback_query(F.data == 'tg_accs_get')
async def get_acc_info(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    accounts = await accs_action.db_get_all_accounts()
    phone_list = [acc['phone'] for acc in accounts]
    proxy_list = [acc['proxy'] for acc in accounts]
    operation = 'get_info'
    await callback.message.answer('<b>Выберите аккаунт:</b>',
                                  reply_markup=main_kb.generate_accs_keyboard(phone_list, operation),
                                  parse_mode='HTML')

@router.callback_query(F.data.startswith('account_get_info'))
async def process_get_acc_info(callback: CallbackQuery):
    uid = callback.from_user.id
    account = callback.data.split('_')[-1]
    acc_lst = [account]
    logger.info(f'account chosen: {account}')
    try:
        cbmsg = await callback.message.answer(f'Запрашиваю информацию об аккаунте {account}...⏳')
        acc_info = await get_info(acc_lst, uid)
        if acc_info:
            for (phone, id, first_name, last_name, username, restricted, about) in acc_info:
                string = ''
                await asyncio.sleep(0.5)
                string += (f'<b>Прокси:</b> Не установлен\n'
                           f'<b>Тел:</b> {phone}\n'
                           f'<b>ID:</b> {id}\n'
                           f'<b>Имя:</b> {first_name}\n'
                           f'<b>Фамилия:</b> {last_name}\n'
                           f'<b>Username:</b> @{username}\n'
                           f'<b>Биография:</b> {about}\n'
                           f'<b>Ограничения:</b> {restricted}\n')
                await cbmsg.edit_text(string, parse_mode='HTML')
                string = ''
        else:
            await callback.message.answer(f'Ошибка при запросе информации об аккаунте {account}'
                                          f'\nПожалуйста, попробуйте позже.')

    except Exception as e:
        logger.error(e)
        await callback.message.answer(f'Ошибка при запросе информации об аккаунте {account}'
                                      f'\nПожалуйста, попробуйте позже.')
        return

# @router.callback_query(F.data == 'tg_accs_get')
# async def get_acc_info(callback: CallbackQuery, state: FSMContext):
#     uid = callback.from_user.id
#
#     logger.info('getting info about TG accounts')
#     await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...')
#     try:
#         accounts = await accs_action.db_get_all_accounts()
#         await asyncio.sleep(1)
#         if accounts:
#             phone_list = [acc['phone'] for acc in accounts]
#             proxy_list = [acc['proxy'] for acc in accounts]
#             acc_info = asyncio.create_task(get_info(phone_list, uid))
#             acc_info = await acc_info
#             await asyncio.sleep(1)
#             if acc_info:
#                 string = ''
#                 for (phone, id, first_name, last_name, username, restricted, about), proxy in zip(acc_info, proxy_list):
#                     await asyncio.sleep(0.5)
#                     proxy = 'Не установлен' if not proxy else proxy
#                     string += (f'<b>Прокси:</b> {proxy}\n'
#                                f'<b>Тел:</b> {phone}\n'
#                                f'<b>ID:</b> {id}\n'
#                                f'<b>Имя:</b> {first_name}\n'
#                                f'<b>Фамилия:</b> {last_name}\n'
#                                f'<b>Username:</b> @{username}\n'
#                                f'<b>Биография:</b> {about}\n'
#                                f'<b>Ограничения:</b> {restricted}\n')
#                     await callback.message.answer(string, parse_mode='HTML')
#                     string = ''
#         else:
#             await callback.message.answer('В базе данных нет телеграм аккаунтов.')
#
#
#     except Exception as e:
#         logger.error(e)
