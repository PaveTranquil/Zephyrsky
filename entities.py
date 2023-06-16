from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton as Button, KeyboardButton as KButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder as Board, ReplyKeyboardBuilder as KBoard

start_board = Board([
    [Button(text='Прогноз погоды', callback_data='weather forecast')],
    [Button(text='Настройки', callback_data='settings')]
]).as_markup()
back_btn = lambda data='', text='': Button(text='🔙 Назад' if not text else text, callback_data=f'back_{data}')

settings_board = Board([
    [Button(text='🗺️ Обновить местоположение', callback_data='send_location')],
    [Button(text='🔔 Настроить уведомления', callback_data='notify_settings')],
    [Button(text='🗑️ Удалить все данные', callback_data='delete_data')],
    [back_btn()]
]).as_markup()
location_board = KBoard([
    [KButton(text='🗺️ Отправить своё местоположение', request_location=True)],
    [KButton(text='🔙 Назад')]
]).as_markup(one_time_keyboard=True, resize_keyboard=True)


START = ('{}{}\n\nС помощью ветров знаний и сил солнца, неба и дождя я предсказываю прогноз погоды на каждый день! '
         'Нажми на кнопку «Прогноз погоды», чтобы узнать прогноз погоды на сегодня, на завтра и даже на целую неделю '
         'вперёд. ⛅\n\nТы можешь настроить меня в «Настройках» и указать своё местоположение или время, когда ты '
         'хочешь получать уведомления. 🔔')
SETTINGS = ('Здесь ты можешь обновить своё местоположение или настроить ежедневные уведомления о погоде. ⚙️\n\nЯ за '
            'конфиденциальность, поэтому по желанию ты можешь удалить все данные о себе и заставить меня забыть тебя, '
            'нажав на кнопку «Удалить все данные». 😉')
LOCATION = ('Нажми на кнопку ниже, чтобы отправить своё текущее местоположение, и дальше я всё сделаю за тебя! 🔍\n\n'
            'Или можешь нажать на 📎 и поделиться местоположением так, если хочешь указать другое.\n\nНу и, наконец, '
            'можешь просто отправить мне название города.')
LOCATION_SET = 'Я запомнил, где ты живёшь ;) Приятно познакомиться с жителем {}! 🤝'
LOCATION_ERROR = 'Я старался, но не смог найти твой город. 😩 Может быть, где-то опечатка? Попробуй ещё раз ;)'
DATA_DELETED = 'Ой, кто-то сверкнул у меня перед лицом Нейрализатором из «Людей в чёрном»... Я всё забыл про тебя...'


@dataclass
class CallbackData:
    data: str
    message: Message


class Dialog(StatesGroup):
    get_geo = State()
    get_notify_time = State()
