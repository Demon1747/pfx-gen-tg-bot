import asyncio

from config import bot, dispatcher
from handlers import default_router, user_router


async def main():
    """
    Инициализация бота 
    """

    # Подключение роутера к диспетчеру
    dispatcher.include_routers(default_router, user_router)

    # Не обрабатываем данные, которые приходили на сервер до включения бота
    await bot.delete_webhook(drop_pending_updates=True)

    # Получение данных с сервера
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot has been stopped')
