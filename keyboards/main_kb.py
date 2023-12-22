from aiogram.utils.keyboard import InlineKeyboardBuilder

def start_btns():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запустить', callback_data='bot_start')
    kb_builder.button(text='Остановить', callback_data='bot_stop')
    kb_builder.button(text='Рассылки', callback_data='spam_settings')
    kb_builder.button(text='Аккаунты', callback_data='tg_accounts')
    kb_builder.button(text='История', callback_data='get_history')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def spam_settings():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Создать', callback_data='bot_add_task')
    kb_builder.button(text='Удалить', callback_data='bot_del_task')
    kb_builder.button(text='Активные рассылки', callback_data='bot_get_tasks')
    kb_builder.button(text='Список выполненных', callback_data='bot_get_executed_tasks')
    kb_builder.button(text='Назад', callback_data='back_to_main_menu')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def accs_settings_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='tg_accs_add')
    kb_builder.button(text='Удалить', callback_data='tg_accs_del')
    kb_builder.button(text='Прокси', callback_data='tg_accs_proxy')
    kb_builder.button(text='Изменить инфо', callback_data='tg_accs_change_info')
    kb_builder.button(text='Назад', callback_data='back_to_main_menu')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def back_to_settings_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Назад', callback_data='tg_accounts')

def tasks_settings_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить', callback_data='tasks_add')
    kb_builder.button(text='Удалить', callback_data='tasks_del')
    kb_builder.button(text='Текущие задачи', callback_data='get_cur_tasks')
    kb_builder.button(text='Назад', callback_data='back_to_main_menu')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def task_approve():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data='confirm_task_create')
    kb_builder.button(text='Отменить', callback_data='decline_task_create')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def proxy_settings_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Добавить прокси', callback_data='change_proxy')
    kb_builder.button(text='Проверить прокси', callback_data='check_proxy')
    kb_builder.button(text='Назад', callback_data='tg_accounts')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)

def accs_info_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Выбрать аккаунт', callback_data='change_info_choose_acc')
    kb_builder.button(text='Мои аккаунты', callback_data='tg_accs_get')
    kb_builder.button(text='Назад', callback_data='tg_accounts')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)




def generate_accs_keyboard(accs, operation, back='tg_accs_change_info'):
    kb_builder = InlineKeyboardBuilder()

    for acc in accs:
        kb_builder.button(text=acc, callback_data=f'account_{operation}_{acc}')

    kb_builder.button(text='◀️Назад', callback_data=back)
    kb_builder.adjust(1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)

def generate_tasks_keyboard(tasks, operation):
    kb_builder = InlineKeyboardBuilder()

    for task in tasks:
        kb_builder.button(text=str(task), callback_data=f'task_{operation}_{str(task)}')

    kb_builder.button(text='◀️Назад', callback_data='spam_settings')
    kb_builder.adjust(1)  # Расположение кнопок в несколько столбцов

    return kb_builder.as_markup(resize_keyboard=True)



def edit_acc_info(account):
    kb_builder = InlineKeyboardBuilder()
    print('acc_edit_name_' + account)
    kb_builder.button(text='Имя', callback_data=f'acc_edit_name_{account}')
    kb_builder.button(text='Фамилия', callback_data=f'acc_edit_surname_{account}')
    kb_builder.button(text='Username', callback_data=f'acc_edit_username_{account}')
    kb_builder.button(text='Bio', callback_data=f'acc_edit_bio_{account}')
    kb_builder.button(text='Аватар', callback_data=f'acc_edit_avatar_{account}')
    kb_builder.button(text='Очистить аватары', callback_data=f'acc_clear_avatars_{account}')
    kb_builder.button(text='◀️Назад', callback_data=f'tg_accs_change_info')

    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)