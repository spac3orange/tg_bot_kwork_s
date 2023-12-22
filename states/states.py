from aiogram.fsm.state import StatesGroup, State


class AddTgAccState(StatesGroup):
    input_proxy = State()
    input_number = State()
    input_2fa = State()
    input_code = State()


class DelTgAccState(StatesGroup):
    input_number = State()
    update_db = State()


class EditAccInfo(StatesGroup):
    change_name = State()
    change_surname = State()
    change_bio = State()
    change_username = State()


class UserSendPhoto(StatesGroup):
    input_photo = State()


class AddSpamTask(StatesGroup):
    input_date = State()
    input_accounts = State()
    input_message = State()
    input_timing = State()


class DelSpamTask(StatesGroup):
    input_id = State()


class SetProxy(StatesGroup):
    input_proxy = State()


class CheckProxy(StatesGroup):
    input_proxy = State()
