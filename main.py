import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage




API_TOKEN = '8516060079:AAGV-phmub_cv35k8tJ6exOOriiQNH6whgc'  


QUESTIONS = [
    {
        "text": "Использование одного и того же пароля для всех сервисов — это безопасно?",
        "correct": False  
    },
    {
        "text": "Двухфакторная аутентификация (2FA) помогает защитить аккаунт от взлома?",
        "correct": True   
    },
    {
        "text": "Можно ли переходить по подозрительным ссылкам от незнакомцев в Telegram?",
        "correct": False  
    },
    {
        "text": "Публичный Wi-Fi (например, в кафе) безопасен для ввода паролей без использования VPN?",
        "correct": False  
    },
    {
        "text": "Антивирус на компьютере помогает защититься от вредоносных программ?",
        "correct": True   
    },
    {
        "text": "Если пришло письмо 'от банка' с требованием срочно ввести пароль, стоит ли доверять и переходить по ссылке?",
        "correct": False  
    }
]


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


class Quiz(StatesGroup):
    start_quiz = State()  
    question = State()   



def get_yes_no_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="answer_yes")
    builder.button(text="❌ Нет", callback_data="answer_no")
    builder.adjust(2)  
    return builder.as_markup()



@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    await state.update_data(question_index=0, score=0)

    await message.answer(
        "🛡️ *Добро пожаловать в викторину по Информационной безопасности!*\n\n"
        "Вам будет задано 6 вопросов. Отвечайте честно, используя кнопки ниже.",
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
        await event.answer(text, parse_mode="Markdown", reply_markup=get_yes_no_keyboard())
    elif isinstance(event, CallbackQuery):
        
        await event.message.edit_text(text, parse_mode="Markdown", reply_markup=get_yes_no_keyboard())
        await event.answer()  


@dp.callback_query(F.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    answer = callback.data  
    user_choice = True if answer == "answer_yes" else False

    data = await state.get_data()
    q_index = data.get('question_index', 0)
    score = data.get('score', 0)

    
    current_question = QUESTIONS[q_index]
    is_correct = (user_choice == current_question['correct'])

    if is_correct:
        score += 1
        feedback = "✅ Верно!"
    else:
        correct_word = "Да" if current_question['correct'] else "Нет"
        feedback = f"❌ Неверно! Правильный ответ: *{correct_word}*."


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
        comment = "👍 Хороший результат! Но есть куда расти."
    else:
        comment = "📚 Вам стоит подтянуть знания в области защиты данных. Будьте осторожны в интернете!"

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