import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

QUESTIONS = [
    {
        "text": "Что из перечисленного является наиболее надёжным паролем?",
        "options": {
            "a": "123456",
            "b": "qwerty",
            "c": "R7#kLp$2mQ9"
        },
        "correct": "c"
    },
    {
        "text": "Что такое фишинг?",
        "options": {
            "a": "Вид антивируса",
            "b": "Метод кражи данных через поддельные сайты или письма",
            "c": "Способ шифрования файлов"
        },
        "correct": "b"
    },
    {
        "text": "Как лучше всего защитить свой аккаунт в интернете?",
        "options": {
            "a": "Использовать один и тот же пароль везде",
            "b": "Включить двухфакторную аутентификацию",
            "c": "Никогда не выходить из аккаунта"
        },
        "correct": "b"
    },
    {
        "text": "Что делать, если вы получили подозрительное письмо от 'банка' с просьбой ввести данные карты?",
        "options": {
            "a": "Перейти по ссылке и ввести данные",
            "b": "Игнорировать и удалить письмо",
            "c": "Ответить отправителю с просьбой уточнить"
        },
        "correct": "b"
    },
    {
        "text": "Какое расширение у безопасного соединения HTTPS?",
        "options": {
            "a": "Замок в адресной строке",
            "b": "Красное предупреждение",
            "c": "Отсутствие значка"
        },
        "correct": "a"
    },
    {
        "text": "Что из перечисленного является примером вредоносного ПО?",
        "options": {
            "a": "Браузер",
            "b": "Троян",
            "c": "Текстовый редактор"
        },
        "correct": "b"
    }
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Quiz(StatesGroup):
    start_quiz = State()
    question = State()

def get_abc_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="A", callback_data="answer_a")
    builder.button(text="B", callback_data="answer_b")
    builder.button(text="C", callback_data="answer_c")
    builder.adjust(3)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(question_index=0, score=0)
    await message.answer(
        "Викторина по Информационной безопасности\n\n"
        "Вам будет задано 6 вопросов с тремя вариантами ответов (a, b, c).\n"
        "Выберите правильный вариант, нажав на кнопку."
    )
    await ask_question(message, state)

async def ask_question(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('question_index', 0)

    if q_index >= len(QUESTIONS):
        await show_result(event, state)
        return

    question = QUESTIONS[q_index]
    text = f"Вопрос {q_index + 1}/{len(QUESTIONS)}:\n{question['text']}\n\n"
    for opt_letter, opt_text in question["options"].items():
        text += f"{opt_letter}. {opt_text}\n"

    if isinstance(event, Message):
        await event.answer(text, reply_markup=get_abc_keyboard())
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=get_abc_keyboard())
        await event.answer()

@dp.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    answer = callback.data[-1]
    user_choice = answer

    data = await state.get_data()
    q_index = data.get('question_index', 0)
    score = data.get('score', 0)

    current_question = QUESTIONS[q_index]
    is_correct = (user_choice == current_question['correct'])

    if is_correct:
        score += 1
        feedback = "Верно!"
    else:
        correct_letter = current_question['correct']
        correct_text = current_question['options'][correct_letter]
        feedback = f"Неверно! Правильный ответ: {correct_letter}. {correct_text}."

    await state.update_data(question_index=q_index + 1, score=score)
    await callback.message.answer(feedback)
    await ask_question(callback, state)

async def show_result(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = len(QUESTIONS)

    if score == total:
        comment = "Идеально! Вы настоящий эксперт по кибербезопасности!"
    elif score >= total - 2:
        comment = "Хороший результат! Но есть куда расти."
    else:
        comment = "Вам стоит подтянуть знания в области защиты данных. Будьте осторожны в интернете!"

    result_text = (
        f"Викторина завершена!\n\n"
        f"Ваш результат: {score} из {total}\n"
        f"{comment}\n\n"
        f"Хотите попробовать снова? Напишите /start"
    )

    await state.clear()

    if isinstance(event, Message):
        await event.answer(result_text)
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(result_text)
        await event.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
