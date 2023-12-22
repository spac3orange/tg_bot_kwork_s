**Установка**

Создаем виртуальное окружение и активируем его

*python -m venv venv*

*venv/Scripts/activate*

Устанавливаем зависимости

*pip install -r requirements.txt*

Создаем файл .env и заполняем его по примеру файла env example.txt

BOT_TOKEN - токен бота, полученный в телеграм у BotFather

ADMIN_ID - ID Администратора бота. Свой ID можно узнать в боте @userinfobot

Запускаем бота

*python bot.py*