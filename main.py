import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy import text, select

from config import settings
from database import async_engine, async_session
from models import Base, Staff, Person

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


class NewStaff(StatesGroup):
    full_name = State()
    gender = State()


class NewPerson(StatesGroup):
    full_name = State()
    date_of_birth = State()
    department = State()
    room = State()


@dp.message(NewStaff.full_name)
async def new_staff_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    builder = InlineKeyboardBuilder()
    builder.button(text='🚹Мужской', callback_data='male')
    builder.button(text='🚺Женский', callback_data='female')
    await message.answer('Выберите Ваш пол:👇', reply_markup=builder.as_markup())
    await state.set_state(NewStaff.gender)


@dp.callback_query(NewStaff.gender, F.data.in_(['male', 'female']))
async def new_staff_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data
    await state.update_data(gender=gender)
    data = await state.get_data()
    last_name, first_name, patronymic = data.get("full_name").split()
    new_staff = Staff(
        tg_id=callback.from_user.id,
        last_name=last_name,
        first_name=first_name,
        patronymic=patronymic,
        gender=gender
    )
    async with async_session() as session:
        session.add(new_staff)
        await session.commit()
    await callback.message.answer('✅Регистрация завершена. Теперь можете выбрать любой пункт ниже👇')
    await callback.answer()
    await state.clear()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        stmt = select(Staff).where(Staff.tg_id == message.from_user.id)
        staff = await session.scalar(stmt)
        if not staff:
            await message.answer(
                'Для начала давайте познакомимся😊. 📝Введите Ваше ФИО (например, <b>Иванов Иван Иванович</b>):',
                parse_mode=ParseMode.HTML)
            await state.set_state(NewStaff.full_name)


@dp.message(Command('new_person'))
async def new_person(message: Message, state: FSMContext):
    await message.answer('📝Введите ФИО постояльца (например, <b>Иванов Иван Иванович</b>):',
                         parse_mode=ParseMode.HTML)
    await state.set_state(NewPerson.full_name)


@dp.message(NewPerson.full_name)
async def new_person_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await message.answer('📝Введите его 📆дату рождения (например, <b>03.08.1938</b>):',
                         parse_mode=ParseMode.HTML)
    await state.set_state(NewPerson.date_of_birth)


@dp.message(NewPerson.date_of_birth)
async def new_person_date_of_birth(message: Message, state: FSMContext):
    try:
        date_of_birth = datetime.strptime(message.text.strip(), '%d.%m.%Y').date()
        if date_of_birth < datetime(1900, 1, 1).date() or date_of_birth > datetime.now().date():
            raise ValueError
        await state.update_data(date_of_birth=date_of_birth)
        builder = InlineKeyboardBuilder()
        builder.button(text='1️⃣', callback_data='dp1')
        builder.button(text='2️⃣', callback_data='dp2')
        builder.button(text='3️⃣', callback_data='dp3')
        builder.button(text='4️⃣', callback_data='dp4')
        await message.answer('🏥На какое отделение он принимается?👇', reply_markup=builder.as_markup())
        await state.set_state(NewPerson.department)
    except ValueError:
        await message.answer('❌Некорректная дата. Используйте формат ДД.ММ.ГГГГ')


@dp.callback_query(NewPerson.department, F.data.in_(['dp1', 'dp2', 'dp3', 'dp4']))
async def new_person_department(callback: CallbackQuery, state: FSMContext):
    department = int(callback.data[-1])
    await state.update_data(department=department)
    await callback.message.answer('🛏Укажите номер комнаты, к которой он прикреплён (1-10):')
    await state.set_state(NewPerson.room)


@dp.message(NewPerson.room)
async def new_person_room(message: Message, state: FSMContext):
    try:
        room = int(message.text.strip())
        if room in range(1, 11):
            data = await state.get_data()
            last_name, first_name, patronymic = data.get("full_name").split()
            new_person = Person(
                last_name=last_name,
                first_name=first_name,
                patronymic=patronymic,
                date_of_birth=data["date_of_birth"],
                department=data["department"],
                room=room
            )
            async with async_session() as session:
                session.add(new_person)
                await session.commit()
            await message.answer('✅Постоялец успешно добавлен')
            await state.clear()
        else:
            await message.answer("❌Кабинет должен быть от 1 до 10")
    except ValueError:
        await message.answer('❌Введите целое число от 1 до 10')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
