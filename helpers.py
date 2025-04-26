from pathlib import Path
from json import load
import importlib.util
import requests
import datetime
import sys
import os

DATETIME = datetime.datetime.now()

def import_module(path):
    """
        Хелпер нужен для динамической подгрузки модулей и по сути заменяет инструкцию import
    """
    # Определяем полный путь к файлу
    file_path = os.path.abspath(path)

    # Получаем имя модуля (без расширения .py)
    module_name = os.path.basename(file_path).replace(".py", "")

    # Загружаем модуль
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    fuzzer_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = fuzzer_module
    spec.loader.exec_module(fuzzer_module)

    return fuzzer_module

def make_request(method: str, url: str, data=None, headers=None):
    """
        Хелпер для обработки запросов вместо вызова requests
    """

    # Загружаем и добавляем куки:
    with open('configs/web.json', 'r') as cookies_file:
        cookies = load(cookies_file)['HTTP']['HEADERS']['COOKIES']

    # Загружаем и добавляем стандартные HTTP заголовки (но они будут перезаписаны теми, которые будут поданы в аргументе функции):
    with open('configs/web.json', 'r') as cookies_file:
        basic_headers = load(cookies_file)['HTTP']['HEADERS']['BASIC']
    if headers is None:
        headers = basic_headers
    else:
        for header_key in basic_headers:
            if header_key not in headers.keys():
                headers[header_key] = basic_headers[header_key]

    if method == 'GET':
        return requests.get(url, cookies=cookies, headers=headers if headers else None)
    elif method == 'POST':
        return requests.post(url, data=data if data else None, cookies=cookies, headers=headers if headers else None)

def check_folder_presense(path: str):
    # Проверяем наличие общей директории с логами. Если ее нет, создаем:
    if not Path(path).is_dir():
        os.mkdir(path)

def log_message(message: str):
    
    path = 'logs'
    log_folder = f'{path}/{DATETIME}'

    # Проверяем наличие общей директории с логами. Если ее нет, создаем:
    check_folder_presense(path)
    # Создаем директорию с логами под текущую сессию работы инструмента:
    check_folder_presense(log_folder)
    
    with open(f'{log_folder}/info.log', 'a') as log_file:
        log_file.write(f'{message}\n')

def log_http(response, alert: str = False, http_type: str = 'request'):
    path = 'logs'
    log_folder = f'{path}/{DATETIME}'

    # Проверяем наличие общей директории с логами. Если ее нет, создаем:
    check_folder_presense(path)
    # Создаем директорию с логами под текущую сессию работы инструмента:
    check_folder_presense(log_folder)

    log = '{}\n{}\r\n{}\r\n\r\n{}'
    # Если нам необходимо добавить запрос, 
    if http_type == 'request':
        log = log.format(
            f'{"-"*50}REQUEST{"-"*50}',
            response.method + ' ' + response.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
            response.body if response.body else '',
        )
    elif http_type == 'response':
        log = log.format(
            f'-{"-"*50}RESPONSE{"-"*50}',
            str(response.status_code) + ' ' + response.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
            response.content.decode() if response.content.decode() else '',
        )
    with open(f'{log_folder}/alerts.log' if alert else f'{log_folder}/traffic.log', 'a') as log_file:
        log_file.write(f'{log}\n')

def check_csrf_presense(html_tags):
    """
        Проверяет наличие csrf в названиях тегов
    """
    html_tags = str(html_tags).replace('[', '').replace(']', '').replace('<', '').replace('>', '').replace('/', '').replace('"', '').replace("'", '').split(', ')
    for tag in html_tags:
        try:
            name_value = tag.split('name=')[1].split(' ')[0]
            if 'csrf' in name_value:
                csrf_token = tag.split('value=')[1].split(' ')[0]
                return {'name': name_value, 'value': csrf_token}
        except IndexError:
            # Предполагаем, что если нет атрибута name, это input
            pass
    return {}

if __name__ == '__main__':
    pass
