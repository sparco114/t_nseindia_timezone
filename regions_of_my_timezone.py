import re

import requests
from requests import Session

url_my_ip = "https://2ip.ru/"
url_my_timezone = "https://www.maxmind.com/en/geoip2-precision-demo"
url_all_timezones_list = ("https://gist.githubusercontent.com/salkar/19df1918ee2aed6669e2/raw"
                          "/84215d4a3fcdfeaabad32e87817ae5bc1073a3b7/Timezones%2520for%2520Russian%2520regions")

my_ip_address = None  # создаем переменную для хранения IP адреса
my_timezone = None  # создаем переменную для хранения timezone
regions_of_my_timezone = None  # создаем переменную для хранения списка регионов таймзоны пользователя

# пробуем получить IP текущего пользователя
try:
    take_my_ip_response = requests.get(url_my_ip)
    take_my_ip_response.raise_for_status()  # если статус ответа укажет на ошибку - вызываем исключение

    # находим начало и конец кода, внутри которого содержится IP адрес
    #  (можно написать с помощью bs4 для динамического поиска)
    start_ip_div = take_my_ip_response.text.find('<div class="ip" id="d_clip_button">')
    start_ip_span = take_my_ip_response.text.find('<span>', start_ip_div)
    end_ip_span = take_my_ip_response.text.find('</span>', start_ip_span)

    # получаем значение IP адреса
    content_my_ip_address = take_my_ip_response.text[start_ip_span + len('<span>'):end_ip_span]

    ip_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")  # шаблон для проверки формата IP адреса

    # проверяем соответствие полученного IP нашему шаблону
    if bool(ip_pattern.match(content_my_ip_address)):
        my_ip_address = content_my_ip_address
    else:
        ValueError("IP адрес имеет некорректный формата")

except Exception as err:
    print(f"Не удалось получить IP адрес текущего пользователя на сайте {url_my_ip}.\n"
          f"Ошибка: {type(err)} - {err}")

# если IP получен, далее пробуем получить time zone текущего пользователя
if my_ip_address:
    try:
        # открываем сессию, т.к. для получения токена необходимо сделать несколько запросов в рамках одной сессии
        with Session() as session:

            # первый запрос на сайт для открытия сессии, из которого так же получим CSRF token
            csrf_token_req = session.get(url_my_timezone)
            csrf_token_req.raise_for_status()

            # находим начало и конец кода, внутри которого содержится CSRF token
            #  (можно написать с помощью bs4 для динамического поиска)
            start_csrf_token = csrf_token_req.text.find('X_CSRF_TOKEN = "')
            end_csrf_token = csrf_token_req.text.find('";', start_csrf_token)
            csrf_token = csrf_token_req.text[start_csrf_token + len('X_CSRF_TOKEN = "'):end_csrf_token]

            # записываем полученный CSRF токен в заголовки
            headers_with_csrf = {'X-CSRF-Token': csrf_token}

            # адрес для получения токена
            url_my_timezone_token = "https://www.maxmind.com/en/geoip2/demo/token"

            # создаем запрос на получение токена, передавая в заголовках полученный CSRF токен
            token_req = session.post(url_my_timezone_token, headers=headers_with_csrf)

            # если получен ответ о создании токена
            if token_req.status_code == 201:
                token = token_req.json()["token"]

                # формируем адрес для получения time zone пользователя
                url_timezone = f"https://geoip.maxmind.com/geoip/v2.1/city/{my_ip_address}?demo=1"

                # добавляем полученный токен в заголовки
                headers_with_token = {'Authorization': f"Bearer {token}"}

                my_timezone_req = session.get(url_timezone, headers=headers_with_token)
                my_timezone_req.raise_for_status()  # если статус ответа укажет на ошибку - вызываем исключение

                # получаем значение timezone из ответа
                my_timezone = my_timezone_req.json()['location']['time_zone']

    except Exception as err:
        print(f"Не удалось получить time_zone текущего пользователя на сайте {url_my_ip}.\n"
              f"Ошибка: {type(err)} - {err}")

if my_timezone:
    # пробуем получить все регионы таймзоны пользователя
    try:
        timezones_list_req = requests.get(url_all_timezones_list)
        timezones_list_req.raise_for_status()

        # получаем список всех таймзон с регионами
        timezones_list = timezones_list_req.json()

        # выбираем все регионы с полученной таймзоной
        regions_of_my_timezone = list(map(lambda x: x[0], filter(lambda x: x[1] == my_timezone, timezones_list)))

    except Exception as err:
        print(f"Не удалось получить time_zone текущего пользователя на сайте {url_my_ip}.\n"
              f"Ошибка: {type(err)} - {err}")

# если значение regions_of_timezone изменилось с None на любое (в т.ч. и на пустой список) - формируем файл
if regions_of_my_timezone is not None:
    with open("regions_of_my_timezone.txt", 'w') as result_file:
        result_file.write(my_timezone + '\n')  # записываем таймзону
        if regions_of_my_timezone != []:
            result_file.write(', '.join(regions_of_my_timezone))  # записываем регионы, если их список не пуст
        else:
            result_file.write(f"Отсутствует информация о регионах для таймзоны '{my_timezone}'")

else:
    print("Не удалось получить список регионов таймзоны пользователя")
