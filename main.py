import requests
import json
import datetime


def get_url_departure():
    url_ya = "https://api.rasp.yandex.net/v3.0/schedule/?"
    api_key = "b98c0fb3-3747-495b-b18c-027cae7c81c0"
    station = "9600380"  # KUF Курумоч Самара
    time_zone = "Europe/Samara"
    today_date = datetime.datetime.today().date()
    return f'{url_ya}apikey={api_key}&station=s{station}&date={today_date}&result_timezone={time_zone}'


def get_url_arrival():
    return f'{get_url_departure()}&event=arrival'


def schedule_parser(json_ds_response):
    for schedule in json_ds_response['schedule']:
        print(schedule['arrival'] or schedule['departure'])
        print(schedule['thread']['title'])
        print()


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


if __name__ == "__main__":
    urls = [get_url_departure(), get_url_arrival()]
    for url in urls:
        json_ds_response = json.loads(get_response(url))
        schedule_parser(json_ds_response)
        print('_'*50)
