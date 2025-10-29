import os

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Файл с переменными окружения находится в директории проекта
env_file_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '.env')


class Settings():
    """ Класс, содержащий основные настройки бота: токен и список пользователей """
    token = ''
    admin_ids = []

    def __init__(self):
        # Загрузка переменных окружения из файла .env
        load_dotenv(override=True,
                    dotenv_path=env_file_path)

        self.token = os.getenv('BOT_TOKEN')
        self.user_ids = [int(elem) for elem in os.getenv('USERS').split(',')]


# Инициализация настроек
settings = Settings()

# Инициализация объекта бота
bot = Bot(token=settings.token)

# Инициализация диспетчера, обрабатывающего обновления с сервера и фильтрующего сообщения
dispatcher = Dispatcher(storage=MemoryStorage())
