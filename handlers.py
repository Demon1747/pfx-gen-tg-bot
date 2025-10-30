from aiogram import Router

from aiogram.filters import Filter, CommandStart, Command
from aiogram.types import Message

from config import settings


class ChatFilter(Filter):
    """ Класс фильтра для ограничения типа чата и списка пользователей """

    # Передача типов чатов, в которых работа роутера разрешена
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # Проверка на присутствие типа чата в списке разрешенных и наличия id пользователя в списке разрешенных
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types and message.from_user.id in settings.user_ids


# Роутер для общего взаимодействия с ботом
default_router = Router()

# Роутер для пользователя
user_router = Router()

# Установка для пользовательского роутера фильтра на личные сообщения
user_router.message.filter(
    ChatFilter(['private'])
)


@default_router.message(CommandStart())
async def user_start_cmd(message: Message):
    """ Команда для всех: позволяет получить id пользователя """
    await message.answer(f'Приветствую, {message.from_user.full_name}! Твой id: {message.from_user.id}')


@user_router.message(Command('gen_pfx'))
async def user_gen_pfx(message: Message):
    """ Команда для начала процесса генерации pfx """
    await message.answer(f'Lets go')
