from os import system

from aiogram import F, Router

from aiogram.filters import Command, CommandStart, Filter
from aiogram.types import CallbackQuery, FSInputFile, Message

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Внутренние зависимости проекта
from config import bot, settings
import keyboards


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
    common_name = State()
    cont_name = State()
    keysize = State()
    file_name = State()


@default_router.message(CommandStart())
async def user_start_cmd(msg: Message):
    """ Команда для всех: позволяет получить id пользователя """
    await msg.answer(f'Приветствую, {msg.from_user.full_name}! Твой id: {msg.from_user.id}')


@user_router.message(Command('gen_pfx'))
async def user_gen_pfx(msg: Message, state: FSMContext):
    """ Команда для начала процесса генерации pfx """
    await state.set_state(PfxParameters.common_name)
    await msg.answer('Введите Common Name для сертификата')


@user_router.message(PfxParameters.common_name)
async def get_cert_cn(msg: Message, state: FSMContext):
    """ Получение у пользователя CN сертификата """
    await state.update_data(common_name=msg.text)
    await state.set_state(PfxParameters.cont_name)
    await msg.answer('Введите название для ключевого контейнера')


@user_router.message(PfxParameters.cont_name)
async def get_cont_name(msg: Message, state: FSMContext):
    """ Получение у пользователя названия контейнера """
    await state.update_data(cont_name=msg.text)
    await state.set_state(PfxParameters.keysize)
    await msg.answer(text='Выберите длину открытого ключа',
                     reply_markup=keyboards.keysize)


# Коллбэки, определяющие длину ключа
@user_router.callback_query(F.data == 'select_512_bit')
async def cb_query_select_512_bit(callback: CallbackQuery, state: FSMContext):
    """ Выбор длины ключа в 512 бит """
    await callback.answer()
    await state.update_data(keysize='-provtype 80 -keysize 512')
    await callback.message.answer(text='Выберите тип ключа', reply_markup=keyboards.key_purpose)


@user_router.callback_query(F.data == 'select_1024_bit')
async def cb_query_select_1024_bit(callback: CallbackQuery, state: FSMContext):
    """ Выбор длины ключа в 1024 бит """
    await callback.answer()
    await state.update_data(keysize='-provtype 81 -keysize 1024')
    await callback.message.answer(text='Выберите тип ключа', reply_markup=keyboards.key_purpose)


# Коллбэки, определяющие назначение ключа
@user_router.callback_query(F.data == 'select_ex')
async def cb_query_select_ex(callback: CallbackQuery, state: FSMContext):
    """ Выбор ключа обмена """
    await callback.answer()
    await state.update_data(purpose='-ex')
    await state.set_state(PfxParameters.file_name)
    await callback.message.answer('Введите название файла для pfx-контейнера (без расширения .pfx)')


@user_router.callback_query(F.data == 'select_sg')
async def cb_query_select_sg(callback: CallbackQuery, state: FSMContext):
    """ Выбор ключа подписи """
    await callback.answer()
    await state.update_data(purpose='-sg')
    await state.set_state(PfxParameters.file_name)
    await callback.message.answer('Введите название файла для pfx-контейнера (без расширения .pfx)')


@user_router.callback_query(F.data == 'select_both')
async def cb_query_select_both(callback: CallbackQuery, state: FSMContext):
    """ Выбор ключа обмена и подписи """
    await callback.answer()
    await state.update_data(purpose='-both')
    await state.set_state(PfxParameters.file_name)
    await callback.message.answer('Введите название файла для pfx-контейнера (без расширения .pfx)')


@user_router.message(PfxParameters.file_name)
async def gen_and_send_pfx(msg: Message, state: FSMContext):
    """ Окончательная генерация pfx """
    await state.update_data(file_name=msg.text)

    # Получение данных из машины состояний и очистка состояния
    cmd_args = await state.get_data()
    await state.clear()

    # Установка аргументов для команд в переменные
    common_name = cmd_args['common_name']
    keysize = cmd_args['keysize']
    cont_name = '\\\\.\\REGISTRY\\' + cmd_args['cont_name']
    purpose = cmd_args['purpose']
    file_name = cmd_args['file_name']

    # Команда для запроса сертификата в УЦ
    gen_command = f'.\\cryptcp.exe -createcert -rdn "CN={common_name}" {keysize} -cont "{cont_name}" {purpose} -silent -ku -du -exprt'
    system(gen_command)

    # Команда для экспорта pfx в файл
    export_command = f'.\\certmgr.exe -export -dn "CN={common_name}" -pfx -dest ".\\files\\{file_name}" -silent'
    system(export_command)

    # Отправка готового pfx пользователю
    pfx_file = FSInputFile(f'.\\files\\{file_name}')
    await bot.send_document(chat_id=msg.chat.id, document=pfx_file)
