import pprint
import requests
import datetime
from aiogram import Bot, Dispatcher, executor, types
import bs4
import asyncio
import os

tg_api_key = os.getenv('API_KEY')
if not tg_api_key:
    exit("Error: no token provided")
bot = Bot(token=tg_api_key)
dp = Dispatcher(bot)
url_kuf_dep = "https://kuf.aero/board/?ready=yes"
url_kuf_arr = "https://kuf.aero/board/?type=arr&ready=yes"
plane_status = {'вылетел', 'регистрация закончена', 'регистрация', 'задержан', 'отменен', 'прибыл', 'ожидается'}


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


def kuf_pars(url):
    list1 = kuf_get_data(url)
    list2 = []
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
        combi = list_iin.pop()
        combi_list = combi.replace('Совмещен c ', '').split(', ')
        combi_set.update(combi_list)
        list_iin.append(combi_list)
        if list_iin[2] not in combi_set:
            list2.append(list_iin)
    return list2


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.reply("/departure  -  Вылеты\n\nor\n\n/arrival  -  Прилёты")


@dp.message_handler(commands="departure")
async def cmd_start(message: types.Message):
    answer = f'{dep_list[0][1]}.{datetime.datetime.today().year}\n\n'
    for x in dep_list:
        answer = f'{answer}{x[0]}\n{x[4]}\n\n'
    await message.answer(answer)


@dp.message_handler(commands="arrival")
async def cmd_start(message: types.Message):
    answer = f'{arr_list[0][1]}.{datetime.datetime.today().year}\n\n'
    for x in arr_list:
        answer = f'{answer}{x[0]}\n{x[4]}\n\n'
    await message.answer(answer)


async def main():
    global dep_list
    global arr_list
    while True:
        dep_list = kuf_pars(url_kuf_dep)
        arr_list = kuf_pars(url_kuf_arr)
        await asyncio.sleep(3)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    asyncio.ensure_future(executor.start_polling(dp, skip_updates=True))
    loop.run_forever()
