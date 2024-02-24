from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums.parse_mode import ParseMode
from aiogram import F

from models import (set_models_id, set_models_name,
                    set_models_surname, set_models_plus,
                    select_models_fullname)

router = Router()


class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    date = State()


@router.message(CommandStart())
async def start(message: types.Message):
    await message.delete()

    markup = InlineKeyboardBuilder()
    markup.add(types.InlineKeyboardButton(
        text='Начать',
        callback_data='ready'
    ))

    await set_models_id(int(message.from_user.id))

    await message.answer('Привет! Я твой староста 🫡\n\nСейчас занесу твои данные в журнал 📖',
                         reply_markup=markup.as_markup())


@router.callback_query(F.data.in_({'ready', 'repeat'}))
async def call_ready(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Напиши свое <b>Имя</b>', parse_mode=ParseMode.HTML)

    await state.set_state(RegisterState.first_name)


@router.callback_query(F.data == 'cancel')
async def cmd_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Отменил действие 🔁')


@router.message(RegisterState.first_name)
async def text_name(message: types.Message, state: FSMContext):
    if message.text.isalpha():
        await set_models_name(message.text, int(message.from_user.id))

        await message.answer('Принято! Напиши свою <b>Фамилию</b>', parse_mode=ParseMode.HTML)

        await state.set_state(RegisterState.last_name)
    else:
        await message.answer('Введи корректное <b>Имя</b> ❌', parse_mode=ParseMode.HTML)


@router.message(RegisterState.last_name)
async def text_surname(message: types.Message, state: FSMContext):
    if message.text.isalpha():
        markup = InlineKeyboardBuilder()
        markup.add(types.InlineKeyboardButton(
            text='Обновить данные',
            callback_data='repeat'
        ))

        await set_models_surname(message.text, int(message.from_user.id))

        await message.answer(
            'Принято! Регистрация прошла успешно ✅\n\nТеперь каждый раз, когда ты присутствуешь '
            'на паре, тебе нужно отправить "+", чтобы я смог тебя отметить 👀',
            reply_markup=markup.as_markup())

        await state.clear()
    else:
        await message.answer('Введи корректную <b>Фамилию</b> ❌', parse_mode=ParseMode.HTML)


@router.message(F.text == '+')
async def plus_command(message: types.Message):
    if await select_models_fullname(message.from_user.id):
        result = await set_models_plus(int(message.from_user.id), message.text)
        if result == 'Сейчас нельзя отметиться':
            await message.answer('Пара еще не началась или уже закончилась - пока отметиться нельзя 🔒')
        elif result == 'Уже есть отметка':
            await message.answer('Уже отметился (-ась) ✅')
        else:
            await message.answer(result)
    else:
        await message.answer('Сначала нужно зарегистрироваться ⚠️')


@router.message()
async def more_message(message: types.Message):
    await message.answer('Неверная команда 🚫')
