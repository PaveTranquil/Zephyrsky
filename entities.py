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

time_board = lambda h=None, m=None: lambda data='', text='': Board(
    [[Button(text='Часы: ↘️' if h is None else f'Часы: {h:02} ↘️', callback_data='show_h')],
     [Button(text='Минуты: ↘️' if m is None else f'Минуты: {m:02} ↘️', callback_data='show_m')],
     [back_btn(data, text)]
     + ([] if h is None or m is None else [Button(text='Создать 🔔', callback_data=f'create_notify {h}:{m}')])]
).as_markup()
hour_board = lambda h=None, m=None: lambda data='', text='': Board(
    [[Button(text='Часы: ↖️' if h is None else f'Часы: {h:02} ↖️', callback_data='hide_h')]]
    + [[Button(text=f'✅ {n:02}' if h == n else f'{n:02}', callback_data=f'set h {n}') for n in range(i, i + 6)]
       for i in range(0, 24, 6)]
    + [[Button(text='Минуты: ↘️' if m is None else f'Минуты: {m:02} ↘️', callback_data='show_m')],
       [back_btn(data, text)]
       + ([] if h is None or m is None else [Button(text='Создать 🔔', callback_data=f'create_notify {h}:{m}')])]
).as_markup()
minute_board = lambda h=None, m=None: lambda data='', text='': Board(
    [[Button(text='Часы: ↘️' if h is None else f'Часы: {h:02} ↘️', callback_data='show_h')]]
    + [[Button(text='Минуты: ↖️' if m is None else f'Минуты: {m:02} ↖️', callback_data='hide_m')]]
    + [[Button(text=f'✅ {n:02}' if m == n else f'{n:02}', callback_data=f'set m {n}') for n in range(i, i + 30, 5)]
       for i in range(0, 60, 30)]
    + [[back_btn(data, text)]
       + ([] if h is None or m is None else [Button(text='Создать 🔔', callback_data=f'create_notify {h}:{m}')])]
).as_markup()


START = ('{}{}\n\nС помощью ветров знаний и сил солнца, неба и дождя я предсказываю прогноз погоды на каждый день! '
         'Нажми на кнопку «Прогноз погоды», чтобы узнать прогноз погоды на сегодня, на завтра и даже на целую неделю '
         'вперёд. ⛅\n\nТы можешь настроить меня в «Настройках» и указать своё местоположение или время, когда ты '
         'хочешь получать уведомления. 🔔')
SETTINGS = ('Здесь ты можешь обновить своё местоположение или настроить ежедневные уведомления о погоде. ⚙️\n\nЯ за '
            'конфиденциальность, поэтому по желанию ты можешь удалить все данные о себе и заставить меня забыть тебя, '
            'нажав на кнопку «Удалить все данные». 😉')
DATA_DELETED = 'Ой, кто-то сверкнул у меня перед лицом Нейрализатором из «Людей в чёрном»... Я всё забыл про тебя...'

CURR_LOCATION = 'Я помню, что ты из {}. 😉'
LOCATION = ('Нажми на кнопку ниже, чтобы отправить своё текущее местоположение, и дальше я всё сделаю за тебя! 🔍\n\n'
            'Или можешь нажать на 📎 и поделиться местоположением так, если хочешь указать другое.\n\nНу и, наконец, '
            'можешь просто отправить мне название города.')
LOCATION_SET = 'Я запомнил, где ты живёшь ;) Приятно познакомиться с жителем {}! 🤝'
LOCATION_ERROR = ('Я старался, но не смог найти твой город. 😩 Может быть, где-то опечатка? Попробуй ещё раз или отправь'
                  ' мне своё местоположение через кнопку ниже или с помощью 📎.')
NO_LOCATION_FORECAST = 'Чтобы предсказать прогноз погоды, мне нужно знать, где ты находишься ;)'

CURR_NOTIFY = ('Список установленных уведомлений: {}\n\nНажми на уведомление ниже, если хочешь его удалить. 🙅🏻‍♂️',
               'Уведомления не установлены.\n\nНажми на кнопку ниже, чтобы установить уведомления. 👇🏻')
NO_LOCATION_NOTIFY = ('Я не смогу отправить тебе уведомление с погодой, потому что не знаю, где ты находишься. 🤷🏻‍♂️ '
                      'Не забудь показать мне в настройках своё местоположение ;)')
NEW_NOTIFY = 'Выбери часы и минуты для уведомления и нажми «Создать» или введи их в формате HH:MM. 🤓'
NOTIFY_ERROR = ('Что-то мне не разобрать, что ты написал. 🤨 Может быть, у тебя где-то ошибочка? Попробуй ещё раз или'
                'воспользуйся клавиатурой ниже ;)')
NOTIFY_SUCCESS = 'Уведомление успешно создано!  🥳'

FORECAST = ('{1} Сегодня в {0} {2}.\n🌡️ На улице {3}°C (ощущается как {4}°C).\n🫠 Давление: {5} мм рт.ст.\n💦 Влажность: '
            '{6}%.\n🍃 {7} ветер скоростью {8} м/c.\n☁️ На небе облачность в {9}%.')

SOON = 'В разработке — ждите очень скоро! 🔜'


@dataclass
class CallbackData:
    data: str
    message: Message


class Dialog(StatesGroup):
    get_geo = State()
    get_notify_time = State()
