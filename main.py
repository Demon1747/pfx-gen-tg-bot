import asyncio

from aiogram.types import BotCommand

from config import bot, dispatcher
from handlers import default_router, user_router


async def main():
    """
    Инициализация бота 
    """

    # Подключение роутера к диспетчеру
    dispatcher.include_routers(default_router, user_router)

    # Список команд
    await bot.set_my_commands([
        BotCommand(command='start', description='Узнать свой user id'),
        BotCommand(command='gen_pfx', description='Сгенерировать pfx')
    ])

    # Не обрабатываем данные, которые приходили на сервер до включения бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Получение данных с сервера
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot has been stopped')
