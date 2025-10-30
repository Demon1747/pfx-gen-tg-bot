from aiogram import Router

from aiogram.filters import Filter, CommandStart, Command
from aiogram.types import Message

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

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


# Список состояний
class PfxParameters(StatesGroup):
    """ Состояния, отражающие процесс заполнения параметров для pfx """
    cn = State()
    cont_name = State()
    keysize = State()
    purpose = State()
    is_exportable = State()
    file_name = State()


@default_router.message(CommandStart())
async def user_start_cmd(msg: Message):
    """ Команда для всех: позволяет получить id пользователя """
    await msg.answer(f'Приветствую, {msg.from_user.full_name}! Твой id: {msg.from_user.id}')


@user_router.message(Command('gen_pfx'))
async def user_gen_pfx(msg: Message, state: FSMContext):
    """ Команда для начала процесса генерации pfx """
    await state.set_state(PfxParameters.cn)
    await msg.answer('Введите Common Name для сертификата')


@user_router.message(PfxParameters.cn)
async def get_pfx_cn(msg: Message, state: FSMContext):
    """ Получение у пользователя CN сертификата """
    await state.update_data(cn=msg.text)
    await state.set_state(PfxParameters.cont_name)
    await msg.answer('Введите название для ключевого контейнера')


@user_router.message(PfxParameters.cont_name)
async def get_pfx_cn(msg: Message, state: FSMContext):
    """ Получение у пользователя названия контейнера """
    await state.update_data(cn=msg.text)
    await state.set_state(PfxParameters.purpose)
    await msg.answer(text='Выберите длину открытого ключа')


@user_router.message(PfxParameters.purpose)
async def get_pfx_cn(msg: Message, state: FSMContext):
    """ Определение назначения ключа с помощью клавиатуры """
    await state.set_state(PfxParameters.is_exportable)
    await msg.answer(text='Выберите назначение ключа')


@user_router.message(PfxParameters.is_exportable)
async def get_pfx_cn(msg: Message, state: FSMContext):
    """ Определение экспортируемости ключа с помощью клавиатуры"""
    await state.set_state(PfxParameters.file_name)
    await msg.answer(text='Введите название файла для pfx-контейнера')


@user_router.message(PfxParameters.file_name)
async def get_pfx_cn(msg: Message, state: FSMContext):
    """ Окончательная генерация pfx """
    await state.update_data(file_name=msg.text)
    await state.clear()

    await msg.answer(text='Успех!')
