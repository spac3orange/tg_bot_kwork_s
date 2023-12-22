import asyncio
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
            await asyncio.sleep(1)
            sess = TelethonConnect(session)
            acc_info = await sess.get_info()
            if acc_info:
                accs_info.append(acc_info)
            else:
                await aiogram_bot.send_message(uid, text=f'Ошибка. Аккаунт <b>{session}</b> не авторизован. ', parse_mode='HTML')
                continue
        except Exception as e:
            print(e)
    print(f'accs_info = {accs_info}')
    return accs_info


@router.callback_query(F.data == 'tg_accs_get')
async def get_acc_info(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id

    logger.info('getting info about TG accounts')
    await callback.message.answer('Запрашиваю информацию о подключенных аккаунтах...')
    try:
        accounts = await accs_action.db_get_all_accounts()
        if accounts:
            phone_list = [acc['phone'] for acc in accounts]
            proxy_list = [acc['proxy'] for acc in accounts]
            acc_info = await get_info(phone_list, uid)
            if acc_info:
                string = ''
                for (phone, id, first_name, last_name, username, restricted, about), proxy in zip(acc_info, proxy_list):
                    await asyncio.sleep(0.5)
                    proxy = 'Не установлен' if not proxy else proxy
                    string += (f'<b>Прокси:</b> {proxy}\n'
                               f'<b>Тел:</b> {phone}\n'
                               f'<b>ID:</b> {id}\n'
                               f'<b>Имя:</b> {first_name}\n'
                               f'<b>Фамилия:</b> {last_name}\n'
                               f'<b>Username:</b> @{username}\n'
                               f'<b>Биография:</b> {about}\n'
                               f'<b>Ограничения:</b> {restricted}\n')
                    await callback.message.answer(string, parse_mode='HTML')
                    string = ''
        else:
            await callback.message.answer('В базе данных нет телеграм аккаунтов.')


    except Exception as e:
        logger.error(e)
