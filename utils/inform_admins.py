from config import aiogram_bot, config_aiogram

async def inform_admins(message_text, reply_markup=None, parse_mode=None):
    admin_list = config_aiogram.admin_id
    print(admin_list)
    for a in admin_list:
        a = int(a)
        if message_text and reply_markup and parse_mode:
            await aiogram_bot.send_message(a, message_text, reply_markup=reply_markup, parse_mode=parse_mode)
        elif message_text and parse_mode:
            await aiogram_bot.send_message(a, message_text, parse_mode=parse_mode)
        elif message_text:
            await aiogram_bot.send_message(a, message_text)