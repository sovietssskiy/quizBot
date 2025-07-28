from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

def generate_options_keyboard(answer_options):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=f"user_answer:{option}")
        )

    builder.adjust(1)
    return builder.as_markup()