import pprint
import requests
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
import bs4
import asyncio
import os
import pytz
from database import Database
from flights import Flights
from functools import wraps

tz = pytz.timezone('Europe/Samara')
tg_api_key = os.getenv('API_KEY')
admin_id = int(os.getenv('ADMIN'))
if not tg_api_key:
    exit("Error: no token provided")
if not admin_id:
    exit("Error: no admin id provided")
bot = Bot(token=tg_api_key)
dp = Dispatcher(bot)
url_kuf_dep = "https://kuf.aero/board/?ready=yes"
url_kuf_arr = "https://kuf.aero/board/?type=arr&ready=yes"
plane_status = {'вылетел', 'регистрация закончена', 'регистрация', 'задержан', 'отменен', 'прибыл', 'ожидается', 'посадка закончена', 'посадка'}
plane_status_minimal = {'задержан', 'отменен', 'прибыл'}
plane_status_other = plane_status.difference(plane_status_minimal)
db = Database()


def get_name(func):
    @wraps(func)
    async def get_name_wrapper(message: types.Message):
        user_id = message.from_user['id']
        username = message.from_user['username'] if message.from_user['username'] is not None else ""
        firstname = message.from_user['first_name'] if message.from_user['first_name'] is not None else ""
        user_name = f'{firstname}@{username}'
        db.edit_name(user_id, user_name)
        return await func(message)
    return get_name_wrapper


def get_response(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        send_admin(f'(get_response) HTTP error occurred: {http_err}')
    except Exception as err:
        send_admin(f'(get_response) Other error occurred: {err}')
    else:
        return response.text


def kuf_get_data(url):
    text = get_response(url)
    soup = bs4.BeautifulSoup(text, "lxml")
    rows = soup.findAll("a", class_="table-flex__row table-flex__row--link align-center")
    list1 = []
    for dat in rows:
        if dat.find('span', class_="board__text") is not None:
            list1.append(dat.text.split('\n'))
    return list1


def kuf_pars(url, arr_flag):
    list1 = []
    try:
        list1 = kuf_get_data(url)
    except Exception as err:
        send_admin(f'(kuf_pars) kuf_get_data {err}')
    res_dict = {}
    combi_set = set()
    for roww in list1:
        list_iin = []
        for i, x in enumerate(roww):
            if i == 19 and x.lower() not in plane_status:
                list_iin.append('Ожидаем')
            if x != '':
                list_iin.append(x.strip())
        if len(list_iin) == 9:
            list_iin.append('')
        list_iin[1] = f'{list_iin[1]}.{datetime.today().year}'
        list_iin[8] = f'{list_iin[8]}.{datetime.today().year}'
        combi = list_iin.pop()
        combi_list = combi.replace('Совмещен c ', '').split(', ')
        combi_set.update(combi_list)
        list_iin.append(combi_list)
        if arr_flag:
            list_iin[4] = f'{list_iin[4]} - Самара'
        else:
            list_iin[4] = f'Самара - {list_iin[4]}'
        list_iin.append(arr_flag)
        flight = list_iin.pop(2)
        if flight not in combi_set:
            res_dict.setdefault(flight, Flights(*list_iin))
    return res_dict


@dp.message_handler(commands="start")
@get_name
async def cmd_start(message: types.Message):
    exi = db.user_exists(message.from_user['id'])
    if not exi:
        db.add_user(message.from_user['id'])
    try:
        await message.answer("/departure -  Вылеты полный список\n\n" +
                             "/arrival       -  Прилёты полный список\n\n" +
                             "/dep           -  Вылеты короткий список\n\n" +
                             "/arr             -  Прилёты короткий список\n\n" +
                             "/info           -  Инфо", reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="depmode")
@get_name
async def cmd_depmode(message: types.Message):
    user_id = message.from_user['id']
    dep_mode = db.get_dep_mode(user_id)
    if dep_mode == 0:
        dep_mode += 1
        answer = f'Включен режим уведомлений обо всех изменениях в расписании вылетов'

    elif dep_mode == 1:
        dep_mode += 1
        answer = f'Включен минимальный режим уведомлений о вылетах (отменен, задержан)'
    else:
        dep_mode = 0
        answer = f'Уведомления о вылетах выключены'
    db.set_dep_mode(user_id, dep_mode)
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="arrmode")
@get_name
async def cmd_arrmode(message: types.Message):
    user_id = message.from_user['id']
    arr_mode = db.get_arr_mode(user_id)
    if arr_mode == 0:
        arr_mode += 1
        answer = f'Включен режим уведомлений обо всех изменениях в расписании прилётов'

    elif arr_mode == 1:
        arr_mode += 1
        answer = f'Включен минимальный режим уведомлений о прилётах (прибыл, отменен)'
    else:
        arr_mode = 0
        answer = f'Уведомления о прилётах выключены'
    db.set_arr_mode(user_id, arr_mode)
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="departure")
@get_name
async def cmd_departure(message: types.Message):
    answer = ''
    for x in dep_old:
        answer = f'{answer}{dep_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="arrival")
@get_name
async def cmd_arrival(message: types.Message):
    answer = ''
    for x in arr_old:
        answer = f'{answer}{arr_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="dep")
@get_name
async def cmd_dep(message: types.Message):
    answer = ''
    min_time = datetime.now().astimezone(tz) - timedelta(minutes=90)
    max_time = datetime.now().astimezone(tz) + timedelta(minutes=180)
    answer = f'{min_time}\n{max_time}\n'
    for x in dep_old:
        fl_time = dep_old[x].get_rl_date()
        if min_time < fl_time < max_time:
            answer = f'{answer}{dep_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="arr")
@get_name
async def cmd_arr(message: types.Message):
    answer = ''
    min_time = datetime.now().astimezone(tz) - timedelta(minutes=90)
    max_time = datetime.now().astimezone(tz) + timedelta(minutes=180)
    answer = f'{min_time}\n{max_time}\n'
    for x in arr_old:
        fl_time = arr_old[x].get_rl_date()
        if min_time < fl_time < max_time:
            answer = f'{answer}{arr_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="users")
@get_name
async def cmd_users(message: types.Message):
    if message.from_user['id'] == admin_id:
        users = db.get_user_names()
        answer = '\n'.join(map(str, users))
        try:
            await message.answer(f'{len(users)} Пользователей\n{answer}', reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
        except:
            pass


@dp.message_handler(commands="time")
@get_name
async def cmd_time(message: types.Message):
    if message.from_user['id'] == admin_id:
        try:
            await message.answer(f'{datetime.now().astimezone(tz)}', reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
        except:
            pass


@dp.message_handler()
async def recieve_any_text(message: types.Message):
    await cmd_start(message)


async def send_to_user_list(text: str, users: list):
    for user in users:
        try:
            await bot.send_message(int(user), text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.1)


async def send_admin(text: str):
    try:
        await bot.send_message(int(admin_id), text, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


async def eq_flight(old_flights, new_flights):
    for x in new_flights:
        old_flights.setdefault(x, None)
        if old_flights[x] is not None:
            diff = old_flights[x].difference(new_flights[x])
            status = new_flights[x].status.lower()
            ii = 2 if status in plane_status_minimal else 1
            users = []
            if new_flights[x].arr_flag:
                for i in range(1, ii):
                    users = users + db.get_user_list_arr(i)
            else:
                for i in range(1, ii):
                    users = users + db.get_user_list_dep(i)
            if diff == 's':
                await send_to_user_list(f'Поменялся статус рейса:\n{new_flights[x]}', users)
            elif diff == 's+rt':
                await send_to_user_list(f'Поменялось время и статус рейса:\n{new_flights[x]}', users)
            elif diff == 'rt':
                await send_to_user_list(f'Поменялось время рейса:\n{new_flights[x]}', users)


async def main():
    global dep_old
    global arr_old
    dep_old = kuf_pars(url_kuf_dep, False)
    arr_old = kuf_pars(url_kuf_arr, True)
    await asyncio.sleep(20)
    while True:
        dep_new = kuf_pars(url_kuf_dep, False)
        arr_new = kuf_pars(url_kuf_arr, True)
        await eq_flight(dep_old, dep_new)
        dep_old = dep_new
        await eq_flight(arr_old, arr_new)
        arr_old = arr_new
        await asyncio.sleep(20)


if __name__ == "__main__":
    global keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["/info", "/departure", "/arrival", "/dep", "/arr", "/depmode", "/arrmode"]
    keyboard.add(*buttons)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    asyncio.ensure_future(executor.start_polling(dp, skip_updates=True))
    loop.run_forever()
