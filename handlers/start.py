import logging
from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder as Board

from entities import (DATA_DELETED, LOCATION_SET, SETTINGS, START, CallbackData,
                      Dialog, back_btn, settings_board, start_board)
from loader import bot, db
from tools.bot import delete_state, get_greeting
from tools.converters import inflect_city

router = Router(name='start -> router')


@router.callback_query(F.data == 'back_', StateFilter('*'))
@router.message(F.chat.type.in_({'private'}), Command('start'), StateFilter('*'))
async def start(resp: CallbackQuery | Message | CallbackData, state: FSMContext):
    logging.debug('start (resp: %s, state: %s)', resp, state)
    if isinstance(resp, CallbackQuery) or await state.get_data():
        await resp.answer()
        with suppress(TelegramBadRequest):
            await resp.message.delete()
    await delete_state(state)
    msg = resp if isinstance(resp, Message) else resp.message
    uid = msg.chat.id

    if not await db.get_user(uid):
        await db.create_user(uid)
        text = START.format((await get_greeting(uid))[0],
                            f'! Я Зефирски 🖖🏼 А ты, кажется, {msg.chat.first_name}? Приятно познакомиться! 🤝')
    else:
        text = START.format((await get_greeting(uid))[0], f', {msg.chat.first_name}! 🖖🏼')
    await msg.answer(text, reply_markup=start_board)


@router.callback_query(F.data.in_({'settings', 'back_settings'}), StateFilter('*'))
async def settings(call: CallbackQuery | CallbackData, state: FSMContext):
    logging.debug('settings (call: %s, state: %s)', call, state)
    user = await db.get_user(call.message.chat.id)
    if user.state.get('from') == 'settings':
        text = f"{LOCATION_SET.format(inflect_city(user.state.get('city'), {'gent'}))}\n\n{SETTINGS}"
        await call.message.answer(text, reply_markup=settings_board)
    else:
        await call.message.edit_text(SETTINGS, reply_markup=settings_board)
    await db.set_state(call.message.chat.id, 'from', 'settings')


@router.callback_query(F.data == 'back_settings', StateFilter(Dialog.get_geo))
@router.message(F.text == '🔙 Назад', StateFilter(Dialog.get_geo))
async def back_to_settings(msg: Message, state: FSMContext):
    logging.debug('back_to_settings (msg: %s, state: %s)', msg, state)
    await msg.delete()
    service_msg = await bot.send_message(msg.chat.id, 'ㅤ', reply_markup=ReplyKeyboardRemove())
    await service_msg.delete()

    await bot.delete_message(msg.chat.id, await db.get_state(msg.chat.id, 'main_msg_id'))
    if await db.get_state(msg.chat.id, 'from') == 'settings':
        await msg.answer(SETTINGS, reply_markup=settings_board)
    elif await db.get_state(msg.chat.id, 'from') == 'forecast':
        return await start(CallbackData('back_', msg), state)
    elif await db.get_state(msg.chat.id, 'from') == 'notify':
        await msg.answer(SETTINGS, reply_markup=settings_board)
    await delete_state(state)
    await db.set_state(msg.chat.id, 'from', 'settings')


@router.callback_query(F.data == 'delete_data')
async def delete_data(call: CallbackQuery, state: FSMContext):
    logging.debug('delete_data (call: %s, state: %s)', call, state)
    await db.delete_user(call.message.chat.id)
    await call.message.edit_text(DATA_DELETED, reply_markup=Board([[back_btn(text='В главное меню 🏠')]]).as_markup())


@router.callback_query(F.data == 'ok', StateFilter('*'))
async def ok_button(call: CallbackQuery, state: FSMContext):
    logging.debug('ok_button (call: %s, state: %s)', call, state)
    await call.message.delete()


@router.callback_query(F.data.startswith('empty'), StateFilter('*'))
async def idle_handler(call: CallbackQuery, state: FSMContext):
    logging.debug('idle_handler')
    await call.answer()
