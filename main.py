import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from telebot import types



API_TOKEN = '8663582294:AAG6KkdaLnaZ-ZPpOtjbewc5PV3stJ6dG8g'

QUESTIONS = [
    {
        "text": "Что такое фишинг и для чего он нужен? ",
        "options": [
            "A) Программа для взлома паролей",
            "B) Вид мошенничества с целью получения данных",
            "C) Атака направленнная на сервер"
        ], 
        "correct": 1
    },
    {
        "text": "Какой метод атаки основан на психологическом воздействии на человека,а не на взломе программ?",
        "options": [
            "A) DDoS-атака",
            "B) Использование программ-шифровальщиков",
            "C) Социальная инженерия",
            
        ],
        "correct": 2
    },
    {
        "text": "Что такое двухфакторная аутентификация и для чего она нужна?",
        "options": [
            "A) Это проверка пароля два раза подряд",
            "B)Это второй уровень защиты, для потверждения входа.",
            "C) Это автомотическая смена пароля раз в месяц",
            
        ],
        "correct": 1
    },
    {
        "text": "Какие последствия для жертвы может иметь взлом аккаунта в социальной сети",
        "options": [
            "A) Только потеря доступа к странице",
            "B) Кража данных,публикация постов от имени жертвы",
            "C) Замедление работы компьютера ",
            
        ],
        "correct": 1
    },
    {
        "text": "К каким последствиям для бизнеса может привести успешная хакерская атака?",
        "options": [
            "A) Только к временным неудобствам для сотрудников",
            "B) К утечке  данных сотрудников и потери финансов",
            "C) К потери репутации компании",
            
        ],
        "correct": 1
    },
    {
        "text": "Какое правило является самым важным при создании паролей?",
        "options": [
            "A) Пароль должен быть коротким",
            "B) Пароль должен быть сложным и уникальным ",
            "C) Пароль должен содержать  имя с фамилией",
           
        ],
        "correct": 1
    }
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Quiz(StatesGroup):
    start_quiz = State()
    question = State()

def get_options_keyboard(options):
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(options):
        builder.button(text=option, callback_data=f"answer_{i}")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(question_index=0, score=0)
    await message.answer(
        "🛡️ *Добро пожаловать в викторину по Информационной безопасности!*\n\n"
        "Вам будет задано 6 вопросов. Выберите правильный вариант ответа.",
        parse_mode="Markdown"
    )
    await ask_question(message, state)

async def ask_question(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    q_index = data.get('question_index', 0)
    
    if q_index >= len(QUESTIONS):
        await show_result(event, state)
        return

    question = QUESTIONS[q_index]
    text = f"*Вопрос {q_index + 1}/{len(QUESTIONS)}:*\n{question['text']}"

    if isinstance(event, Message):
        await event.answer(text, parse_mode="Markdown", reply_markup=get_options_keyboard(question['options']))
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=get_options_keyboard(question['options']))
        await event.answer()

@dp.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    answer_index = int(callback.data.split("_")[1])
    
    data = await state.get_data()
    q_index = data.get('question_index', 0)
    score = data.get('score', 0)
    
    current_question = QUESTIONS[q_index]
    is_correct = (answer_index == current_question['correct'])
    
    if is_correct:
        score += 1
        feedback = "✅ Верно!"
    else:
        correct_option = current_question['options'][current_question['correct']]
        feedback = f"❌ Неверно! Правильный ответ: *{correct_option}*."

    await state.update_data(question_index=q_index + 1, score=score)
    await callback.message.answer(feedback, parse_mode="Markdown")
    await ask_question(callback, state)

async def show_result(event: Message | CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = len(QUESTIONS)
    
    if score == total:
        comment = "🏆 Идеально! Вы настоящий эксперт по кибербезопасности!"
    elif score >= total - 2:
        comment = " Хороший результат! Но есть куда расти."
    else:
        comment = "Вам стоит быть более отсторожным в интернете"

    result_text = (
        f"📊 *Викторина завершена!*\n\n"
        f"Ваш результат: *{score} из {total}*\n"
        f"{comment}\n\n"
        f"Хотите попробовать снова? Напишите /start"
    )
    
    await state.clear()
    
    if isinstance(event, Message):
        await event.answer(result_text, parse_mode="Markdown")
    elif isinstance(event, CallbackQuery):
        await event.message.edit_text(result_text, parse_mode="Markdown")
        await event.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
