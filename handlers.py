from aiogram import Router

from aiogram.filters import CommandStart
from aiogram.types import Message

from config import settings

# Основной роутер пользователя
user_router = Router()


@user_router.message(CommandStart())
async def user_start_cmd(message: Message):
    """ Позволяет получить id пользователя """
    await message.answer(f'Приветствую, {message.from_user.full_name}! Твой id: {message.from_user.id}')
