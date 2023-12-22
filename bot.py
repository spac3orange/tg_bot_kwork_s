from database import db
import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import aiogram_bot, logger
from keyboards import set_commands_menu
from handlers import (start, accounts_menu, add_tg_acc, del_tg_acc,
                      get_tg_accs, proxy_menu, change_info_menu, spam_settings_menu,
                      create_task, del_task, get_tasks, change_status, pop_up_commands, get_history)
from scheduler import main_scheduler


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(add_tg_acc.router)
    dp.include_router(del_tg_acc.router)
    dp.include_router(get_tg_accs.router)
    dp.include_router(change_info_menu.router)
    dp.include_router(proxy_menu.router)
    dp.include_router(spam_settings_menu.router)
    dp.include_router(create_task.router)
    dp.include_router(del_task.router)
    dp.include_router(get_tasks.router)
    dp.include_router(change_status.router)
    dp.include_router(get_history.router)
    dp.include_router(pop_up_commands.router)
    dp.include_router(accounts_menu.router)
    dp.include_router(start.router)

    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД
    await db.db_start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    await asyncio.sleep(3)
    task2 = asyncio.create_task(main_scheduler.start())
    await asyncio.gather(task1, task2)


if __name__ == '__main__':
    try:
        while True:
            asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped')
    except Exception as e:
        logger.error(e)
