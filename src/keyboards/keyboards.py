from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

some_button1 = InlineKeyboardButton(
    text="Button 1",
    callback_data="first button clicked"
)
some_button2 = InlineKeyboardButton(
    text="Button 2",
    callback_data="second button clicked"
)
some_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [some_button1],
        [some_button2]
    ],
    resize_keyboard=True
)