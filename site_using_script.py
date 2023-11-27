import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
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

    time.sleep(0.5)  # задержка для схожести поведения с пользовательским

    # находим необходимую ссылку на 'NIFTY BANK'
    nifty_bank_link = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@id='tabList_NIFTYBANK']")))

    # переводим курсор и кликаем по 'NIFTY BANK'
    action.move_to_element(nifty_bank_link).pause(0.5).click().perform()

    time.sleep(1.5)  # задержка для схожести поведения с пользовательским

    # находим необходимую ссылку (View All) для просмотра всех активов
    view_all_link = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located(
            (By.XPATH, "//div[@id='tab4_gainers_loosers']//a[./span[@id='viewall']]")))

    # скроллим до найденной ссылки 'View All' (с учетом зафиксированного футера)
    scroll_to_view_all = ScrollOrigin.from_element(view_all_link)
    action.scroll_from_origin(scroll_to_view_all, 0, 100).perform()

    time.sleep(1)  # задержка для схожести поведения с пользовательским

    # переводим курсор и кликаем по 'View All'
    action.move_to_element(view_all_link).pause(0.5).click().perform()

    time.sleep(1)  # задержка для схожести поведения с пользовательским

    # находим выпадающее окно для выбора необходимого индекса
    equitie_stock_select = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//select[@id='equitieStockSelect']")))

    time.sleep(1)  # задержка для схожести поведения с пользовательским

    # переводим курсор и кликаем по выпадающему окну
    action.move_to_element(equitie_stock_select).pause(0.5).click().perform()

    time.sleep(1)  # задержка для схожести поведения с пользовательским

    # находим необходимый индекс 'NIFTY ALPHA 50' для выбора в выпадающем окне
    option_to_select = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//option[@data-nse-translate-symbol='NIFTY ALPHA 50']")))

    # выбираем индекс 'NIFTY ALPHA 50'
    selecting_in_equitie_stock_select = Select(equitie_stock_select)
    selecting_in_equitie_stock_select.select_by_visible_text('NIFTY ALPHA 50')

    # дожидаемся пока строки в таблице активов станут видимыми (с учетом выбранного нового индекса)
    rows = WebDriverWait(driver, 5).until(
        EC.visibility_of_all_elements_located(
            (By.XPATH, "//table[@id='equityStockTable']/tbody[./tr[@class='freezed-row']]/tr")))

    # получаем последнюю строку таблицы активов
    last_row = rows[-1]

    time.sleep(1)  # задержка для схожести поведения с пользовательским

    # скроллим до последней строки таблицы
    action.scroll_to_element(last_row).perform()

    time.sleep(5)  # задержка перед закрытием браузера
