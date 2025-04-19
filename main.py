import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy import text, select

from config import settings
from database import async_engine, async_session
from models import Base, Staff

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


class NewStaff(StatesGroup):
    last_name = State()
    first_name = State()
    patronymic = State()
    gender = State()


@dp.message(NewStaff.last_name)
async def new_staff_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await message.answer('Теперь введите Ваше имя:')
    await state.set_state(NewStaff.first_name)


@dp.message(NewStaff.first_name)
async def new_staff_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.answer('И наконец введите Ваше отчество:')
    await state.set_state(NewStaff.patronymic)


@dp.message(NewStaff.patronymic)
async def new_staff_patronymic(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text.strip())
    builder = InlineKeyboardBuilder()
    builder.button(text='Мужской', callback_data='male')
    builder.button(text='Женский', callback_data='female')
    await message.answer('Выберите Ваш пол:', reply_markup=builder.as_markup())
    await state.set_state(NewStaff.gender)


@dp.callback_query(NewStaff.gender, F.data.in_(['male', 'female']))
async def new_staff_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data
    await state.update_data(gender=gender)
    data = await state.get_data()
    new_staff = Staff(
        tg_id=callback.from_user.id,
        last_name=data['last_name'],
        first_name=data['first_name'],
        patronymic=data['patronymic'],
        gender=gender
    )
    async with async_session() as session:
        session.add(new_staff)
        await session.commit()
    await callback.message.edit_text('Регистрация завершена')
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
            await message.answer('Для начала давайте познакомимся. Введите Вашу фамилию:')
            await state.set_state(NewStaff.last_name)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
