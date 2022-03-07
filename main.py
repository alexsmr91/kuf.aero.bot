import pprint
import requests
import datetime
from aiogram import Bot, Dispatcher, executor, types
import bs4
import asyncio
import os
from database import Database
from flights import Flights

tg_api_key = os.getenv('API_KEY')
if not tg_api_key:
    exit("Error: no token provided")
bot = Bot(token=tg_api_key)
dp = Dispatcher(bot)
url_kuf_dep = "https://kuf.aero/board/?ready=yes"
url_kuf_arr = "https://kuf.aero/board/?type=arr&ready=yes"
plane_status = {'вылетел', 'регистрация закончена', 'регистрация', 'задержан', 'отменен', 'прибыл', 'ожидается', 'посадка закончена', 'посадка'}
db = Database()


def get_response(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
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
    list1 = kuf_get_data(url)
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
        list_iin[1] = f'{list_iin[1]}.{datetime.datetime.today().year}'
        list_iin[8] = f'{list_iin[8]}.{datetime.datetime.today().year}'
        combi = list_iin.pop()
        combi_list = combi.replace('Совмещен c ', '').split(', ')
        combi_set.update(combi_list)
        list_iin.append(combi_list)
        if arr_flag:
            list_iin[4] = f'{list_iin[4]} - Самара'
        else:
            list_iin[4] = f'Самара - {list_iin[4]}'
        flight = list_iin.pop(2)
        if flight not in combi_set:
            res_dict.setdefault(flight, Flights(*list_iin))
    return res_dict


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    exi = db.user_exists(message.from_user['id'])
    if not exi:
        db.add_user(message.from_user['id'])
    try:
        await message.answer("/departure  -  Вылеты\n\nor\n\n/arrival  -  Прилёты", reply_markup=keyboard)
    except:
        pass


@dp.message_handler(commands="departure")
async def cmd_dep(message: types.Message):
    #answer = f'{dep_list[0][1]}\n\n'
    answer = ''
    for x in dep_old:
        answer = f'{answer}{dep_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass


@dp.message_handler(commands="arrival")
async def cmd_arr(message: types.Message):
    #answer = f'{arr_list[0][1]}\n\n'
    answer = ''
    for x in arr_old:
        answer = f'{answer}{arr_old[x]}\n'
    try:
        await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
    except:
        pass

@dp.message_handler(commands="users")
async def cmd_users(message: types.Message):
    if message.from_user['id'] == 140535724:
        answer = '\n'.join(map(str, db.get_user_list()))
        try:
            await message.answer(answer, reply_markup=keyboard, parse_mode=types.ParseMode.HTML)
        except:
            pass


@dp.message_handler()
async def send_all(text: str):
    users = db.get_user_list()
    for user in users:
        try:
            await bot.send_message(int(user), text, parse_mode=types.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.1)


async def eq_flight(old_flights, new_flights):
    for x in new_flights:
        old_flights.setdefault(x, None)
        if old_flights[x] is not None:
            diff = old_flights[x].difference(new_flights[x])
            if diff == 's':
                await send_all(f'Поменялся статус рейса:\n{new_flights[x]}')
            elif diff == 's+rt':
                await send_all(f'Поменялось время и статус рейса:\n{new_flights[x]}')


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
    buttons = ["/departure", "/arrival"]
    keyboard.add(*buttons)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    asyncio.ensure_future(executor.start_polling(dp, skip_updates=True))
    loop.run_forever()
