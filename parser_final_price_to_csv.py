import csv
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROXY_ADDRESS = ""  # Указать адрес прокси (опционально)
PROXY_PORT = ""  # Указать порт прокси (опционально)

chrome_options = webdriver.ChromeOptions()

# отключаем функции видимости автоматического управления браузером
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# если указать адрес и порт для прокси - они будут добавлены в настройки драйвера браузера
if PROXY_ADDRESS and PROXY_PORT:
    proxy = f"{PROXY_ADDRESS}:{PROXY_PORT}"
    chrome_options.add_argument(f'--proxy-server={proxy}')

with webdriver.Chrome(options=chrome_options) as driver:
    error_msg = None  # инициализируем отсутствие сообщений об ошибках

    # пробуем перейти на сайт, навести указатель на MARKET DATA и кликнуть Pre-Open Market
    try:
        # переходим на сайт
        driver.get("https://www.nseindia.com")

        action = ActionChains(driver)

        # пробуем закрыть рекламное окно, если оно появляется
        try:
            ad_window_close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='myModal']//button[@class='close']")))

            time.sleep(1)  # задержка для схожести поведения с пользовательским
            action.move_to_element(ad_window_close_button).pause(0.5).click().perform()

        # если рекламное окно не появилось - отлавливаем исключение и продолжаем выполнение скрипта
        except TimeoutException:
            pass

        time.sleep(1)  # задержка для схожести поведения с пользовательским

        # определяем путь к разделу  'MARKET DATA'
        market_data_xpath = ("//li[contains(@class, 'nav-item') "
                             "and .//a[@class='nav-link dd-link' and text()='Market Data']]")

        # находим раздел 'MARKET DATA' на сайте
        market_data_menu = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, market_data_xpath)))

        # наводим курсор на 'MARKET DATA'
        action.move_to_element(market_data_menu).perform()

        time.sleep(1)  # задержка для схожести поведения с пользовательским

        # находим пункт 'Pre-Open Market' в разделе 'MARKET DATA'
        pre_open_market_link = WebDriverWait(market_data_menu, 3).until(
            EC.element_to_be_clickable((By.XPATH, ".//a[text()='Pre-Open Market']")))

        # кликаем по 'Pre-Open Market'
        action.move_to_element(pre_open_market_link).pause(0.5).click().perform()

    # в случае ошибки заполняем сообщение об ошибке
    except Exception as err:
        error_msg = (f"На странице '{driver.current_url}' не удалось найти ссылку "
                     f"для перехода на 'Pre-Open Market'\n"
                     f"Тип ошибки: '{type(err)}'\n"
                     f"Текст ошибки: '{err}'")

    # в случае удачного перехода на страницу Pre-Open Market
    else:
        # пробуем получить данные об имени и цене актива
        try:
            # получаем перечень всех активов из таблицы
            all_assets = WebDriverWait(driver, 10).until(
                EC.visibility_of_all_elements_located(
                    (By.XPATH, "//table[@id='livePreTable']//tbody//tr[@class='']")))

            result_list_to_csv = []  # список, в который добавим полученные данные об именах и ценах

            # перебираем все активы, чтобы получить пару имя-цена для каждого актива
            for asset in all_assets:
                name = asset.find_element(By.XPATH, './/a[@class="symbol-word-break"]').text
                price = asset.find_element(By.XPATH, './/td[@class="bold text-right"]').text

                # добавляем полученную пару имя-цена в список
                result_list_to_csv.append([name, price])

        # в случае ошибки заполняем сообщение об ошибке
        except Exception as err:
            error_msg = (f"Не удалось корректно получить данные со страницы {driver.current_url}'\n"
                         f"Тип ошибки: '{type(err)}'\n"
                         f"Текст ошибки: '{err}'")

    # в случае наличия ошибок записываем их в файл
    if error_msg:
        with open('error_nseindia_data.log', 'w') as nseindia_data:
            nseindia_data.write(error_msg)

    # в случае отсутствия ошибок записываем в файл данные об именах и ценах
    else:
        with open('nseindia_data.csv', 'w') as nseindia_data:
            file_writer = csv.writer(nseindia_data, delimiter=';')
            file_writer.writerows(result_list_to_csv)

    time.sleep(2)  # задержка перед закрытием браузера
