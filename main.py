import pprint
import requests
import json
import datetime
import telebot

tg_api_key = "5203110638:AAEFnrlYHl0jhs4I8N4UpMqzjMKjcfDTeYQ"
bot = telebot.TeleBot(tg_api_key)


def get_url_departure():
    url_ya = "https://api.rasp.yandex.net/v3.0/schedule/?"
    api_key = "b98c0fb3-3747-495b-b18c-027cae7c81c0"
    station = "9600380"  # KUF Курумоч Самара
    #time_zone = "Europe/Samara"
    today_date = datetime.datetime.today().date()
    return f'{url_ya}apikey={api_key}&station=s{station}&date={today_date}'#&result_timezone={time_zone}'


def get_url_arrival():
    return f'{get_url_departure()}&event=arrival'


def schedule_parser(json_ds_response):
    str_res = f'{datetime.datetime.today().date()}\n\n'
    for schedule in json_ds_response['schedule']:
        time = schedule['arrival'] or schedule['departure']

        time = time[11:16]

        str_res = f"{str_res}{time}\n{schedule['thread']['title']}\n\n"
    return str_res


def get_response(api_url: str):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        return response.text


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/departure":
        bot.send_message(message.from_user.id, schedule_parser(json.loads(get_response(get_url_departure()))))
    elif message.text == "/arrival":
        bot.send_message(message.from_user.id, schedule_parser(json.loads(get_response(get_url_arrival()))))
    else:
        bot.send_message(message.from_user.id, "/departure  -  Вылеты\n\nor\n\n/arrival  -  Прилёты")



if __name__ == "__main__":
    """
    urls = [get_url_departure(), get_url_arrival()]
    for url in urls:
        json_ds_response = 
        pprint.pprint(json_ds_response)
        #schedule_parser(json_ds_response)
        print('_'*50)
    """
    bot.polling(none_stop=True, interval=0)
