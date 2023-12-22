import asyncio
import random
from telethon import TelegramClient, errors
from environs import Env
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChannel
from config.logger import logger
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
import datetime
from telethon.tl.functions.messages import GetHistoryRequest
from datetime import timedelta, datetime
from config import aiogram_bot
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import UsernameOccupiedError
from telethon.tl.functions.photos import GetUserPhotosRequest, DeletePhotosRequest
from telethon.tl.types import InputPhoto
import aiofiles
import database
from utils import inform_admins

class AuthTelethon:
    def __init__(self, phone: str, proxy=None):
        self.phone = phone
        env = Env()
        env.read_env()
        print(env('API_ID'))
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')
        self.session_file = 'config/telethon_sessions/{}.session'.format(self.phone)
        print(self.api_id, self.api_hash, self.phone, type(self.phone))
        if not proxy:
            self.client = TelegramClient(self.session_file, self.api_id, self.api_hash)
        else:
            proxy = self.parse_proxy(proxy)
            print(proxy)
            self.client = TelegramClient(self.session_file, self.api_id, self.api_hash, proxy=proxy)


    def parse_proxy(self, proxy_str: str) -> tuple:
        proxy_parts = proxy_str.split('@')
        user_pass, address = proxy_parts[0], proxy_parts[1]
        user, password = user_pass.split(':')
        proxy = ('socks5', *address.split(':'), user, password)
        return proxy

    async def login_phone(self):
        try:
            logger.info('Attempting to connect')
            await self.client.connect()  # Установить соединение
            await self.client.send_code_request(self.phone)
            logger.info(f'Auth code sent to telegram account {self.phone}')
            return True

        except Exception as e:
            logger.error('Authorization error')
            return False


    async def login_process_code(self, code=None, password=None):
        logger.info('Attempting to sign in...')
        if code:
            if password:
                print(1)
                print(password)
                await self.client.sign_in(phone=self.phone, code=code, password=password)
            else:
                print(2)
                await self.client.sign_in(phone=self.phone, code=code)

        else:
            await self.client.sign_in(password=password)

        if await self.client.is_user_authorized():
            logger.info(f'Signed in in {self.phone}')
            await self.client.disconnect()
            return True

        return True

    async def send_message(self, client, message, username):
        try:
            entity = await client.get_input_entity(username)
            await client(SendMessageRequest(
                peer=entity,
                message=message
            ))
            logger.info('Message sent')
        except Exception as e:
            logger.error(f'Error {e}')


    async def join_group(self, group_link):
        try:
            logger.info(f'Joining channel: {group_link}')
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group or dialog.is_channel]
            for dialog in groups_and_channels:
                dialog = await self.client.get_entity(dialog)
                dialog_username = dialog.username
                print(f'dialog_username: {dialog_username}')
                print(f'dialog_link: {group_link}')
                try:
                    if dialog_username == group_link:
                        self.client.disconnect()
                        return 'already_in_group'
                except Exception as e:
                    logger.error(e)
                    continue

            entity = await self.client.get_entity(group_link)

            await self.client(JoinChannelRequest(entity))
            logger.info('Joined group successfully')
            await self.client.disconnect()
            return 'joined'

        except errors.UserDeactivatedBanError as e:
            logger.error(e)
            return 'banned'
        except Exception as e:
            logger.error(f'Error joining group: {e}')
            await self.client.disconnect()
            return False

    async def change_first_name(self, first_name: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(first_name=first_name))
            logger.info(f'Changed first name to {first_name}')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing first name: {e}')
            await self.client.disconnect()
            return False

    async def change_last_name(self, last_name: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(last_name=last_name))
            logger.info(f'Changed last name to {last_name}')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing last name: {e}')
            await self.client.disconnect()
            return False

    async def change_username(self, username: str):
        try:
            await self.client.connect()
            await self.client(UpdateUsernameRequest(username))
            logger.info(f'Changed username to {username}')
            await self.client.disconnect()
            return 'done'
        except UsernameOccupiedError as e:
            logger.error(f'Error changing username: {e}')
            await self.client.disconnect()
            return 'username_taken'
        except Exception as e:
            logger.error(f'Error changing username: {e}')
            await self.client.disconnect()
            return False

    async def change_bio(self, bio: str):
        try:
            await self.client.connect()
            await self.client(UpdateProfileRequest(about=bio))
            logger.info('Changed bio')
            await self.client.disconnect()
            return True
        except Exception as e:
            logger.error(f'Error changing bio: {e}')
            await self.client.disconnect()
            return False

    async def change_profile_photo(self, photo_path: str):
        try:
            await self.client.connect()
            await self.client(UploadProfilePhotoRequest(
                file=await self.client.upload_file(photo_path)
            ))
            logger.info('Changed profile photo')
            return True
        except Exception as e:
            logger.error(f'Error changing profile photo: {e}')
            await self.client.disconnect()
            return False

    async def delete_all_profile_photos(self):
        await self.client.connect()
        try:
            p = await self.client.get_profile_photos('me')
            print(p)
            for photo in p:
                await self.client(DeletePhotosRequest(
                    id=[InputPhoto(
                        id=photo.id,
                        access_hash=photo.access_hash,
                        file_reference=photo.file_reference
                    )]
                ))
                slp = random.randint(2, 4)
                await asyncio.sleep(slp)
            logger.info(f'avatars deleted for account {self.session_file.split("/")[-1]}"')
        except Exception as e:
            logger.error(f'Error deleting all avatars {e}')
        finally:
            await self.client.disconnect()



class TelethonConnect:
    def __init__(self, session_name, proxy=None):
        self.get_env()
        self.session_name = 'config/telethon_sessions/{}.session'.format(session_name)
        if not proxy:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        else:
            print(proxy)
            proxy = self.parse_proxy(proxy)
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash, proxy=proxy)

    def get_env(self):
        env = Env()
        env.read_env()
        self.api_id = env('API_ID')
        self.api_hash = env('API_HASH')

    def parse_proxy(self, proxy_str: str) -> tuple:
        proxy_parts = proxy_str.split('@')
        user_pass, address = proxy_parts[0], proxy_parts[1]
        user, password = user_pass.split(':')
        proxy = ('socks5', *address.split(':'), user, password)
        return proxy

    async def get_info(self):
        try:
            logger.info(f'Getting info about account {self.session_name}...')
            slp = random.randint(1, 3)
            await asyncio.sleep(slp)
            await self.client.connect()
            if not await self.client.is_user_authorized():
                error = (f'Аккаунт: {self.session_name.split("/")[-1]}'
                         'Ошибка. Пользователь не авторизован.')
                print(error)
                return False
            me = await self.client.get_me()
            full_me = await self.client(GetFullUserRequest(me.username))
            about = full_me.full_user.about or 'Не установлено'
            print(about)
            await self.client.disconnect()

            phone = self.session_name.split('/')[-1].rstrip('.session')
            print(phone)
            print(f'Тел: {me.phone}\n'
                  f'ID: {me.id}\n'
                  f'Ник: {me.username}\n'
                  f'Биография: {about}\n'
                  f'Ограничения: {me.restricted}\n'
                  f'Причина ограничений: {me.restriction_reason}\n')

            return me.phone, me.id, me.first_name, me.last_name, me.username, me.restricted, about
            # full = await self.client(GetFullUserRequest('username'))

        except errors.UserDeactivatedBanError as e:
            logger.error(e)
            acc = self.session_name.split("/")[-1].rstrip('.session')
            asyncio.create_task(database.accs_action.db_add_banned_account(acc))
            adm_mess = f'Аккаунт {acc} заблокирован.'
            await inform_admins(adm_mess)
            return

    async def spam_groups(self, user_message, timing):
        try:
            await self.client.connect()
            dialogs = await self.client.get_dialogs()
            groups_and_channels = [dialog for dialog in dialogs if dialog.is_group]
            for dialog in groups_and_channels:
                try:
                    timing = timing * 60
                    dialog = await self.client.get_entity(dialog)
                    await self.client.send_message(dialog, user_message)
                    print(dialog.to_dict())
                    logger.info(f'Account {self.session_name.split("/")[-1]} successfully sent message to {dialog.title}')
                    await self.write_history(dialog)
                    await asyncio.sleep(timing)

                except Exception as e:
                    logger.error(e)
                    print(e)
                    await self.write_error(dialog, e)
                    continue

        except errors.UserDeactivatedBanError as e:
            logger.error(e)
            acc = self.session_name.split("/")[-1].rstrip('.session')
            asyncio.create_task(database.accs_action.db_add_banned_account(acc))
            adm_mess = f'Аккаунт {acc} заблокирован.'
            await inform_admins(adm_mess)

    async def write_history(self, dialog):
        # Запись отправленного комментария в файл
        async with aiofiles.open(f'history/history_{self.session_name.split("/")[-1].rstrip(".session")}.txt', 'a', encoding='utf-8') as file:
            timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            await file.write(f'\n|{timestamp}:'
                             f'\nАккаунт: {self.session_name.split("/")[-1].rstrip(".session")}'
                             f'\nГруппа: {dialog.title}'
                             f'\nСообщение отправлено')
        asyncio.create_task(database.accs_action.db_increment_comments_sent(self.session_name.split("/")[-1].rstrip(".session")))

    async def write_error(self, dialog, e):
        async with aiofiles.open(f'history/errors_{self.session_name.split("/")[-1].rstrip(".session")}.txt', 'a', encoding='utf-8') as file:
            timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            await file.write(f'\n|{timestamp}'
                             f'\nАккаунт: {self.session_name.split("/")[-1].rstrip(".session")}'
                             f'\nГруппа: {dialog.title}'
                             f'\nОшибка: \n{e}\n\n'
                             f'\nСообщение не отправлено')