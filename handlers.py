from aiogram import Router, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from quiz_kb import generate_options_keyboard
from db import get_quiz_index, update_quiz_index, update_score, get_score
from data import quiz_data

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer("Давайте начнем квиз!")
    await update_quiz_index(message.from_user.id, 0)
    await update_score(message.from_user.id, 0)
    await send_question(message, message.from_user.id)


@router.callback_query(F.data.startswith("user_answer:"))
async def handle_user_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    user_answer = callback.data.split("user_answer:")[1]
    await callback.message.answer(f"Вы выбрали: {user_answer}")

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['options'][quiz_data[current_question_index]['correct_option']]

    if user_answer == correct_option:
        await callback.message.answer("Верно!")
        await update_score(user_id, 1, increment=True)
    else:
        await callback.message.answer(f"Неверно!")

    # Переход к следующему вопросу
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await send_question(callback.message, callback.from_user.id)
    else:
        score = await get_score(user_id)
        await callback.message.answer(f"Квиз завершен! Ваш результат: {score}/{len(quiz_data)}")


async def send_question(message: types.Message, user_id: int):
    current_question_index = await get_quiz_index(user_id)
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts)
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)
@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    score = await get_score(message.from_user.id)
    await message.answer(f"Ваш последний результат: {score}/{len(quiz_data)}")