from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Клавиатура для выбора длины ключа
keysize = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='512 бит', callback_data='select_512_bit')],
    [InlineKeyboardButton(text='1024 бит', callback_data='select_1024_bit')]
])

# Клавиатура для выбора назначачения ключа
key_purpose = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Обмена', callback_data='select_ex')],
    [InlineKeyboardButton(text='Подписи', callback_data='select_sg')],
    [InlineKeyboardButton(text='Обмена и подписи',
                          callback_data='select_both')]
])
