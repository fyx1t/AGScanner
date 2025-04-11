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

    Хелпер для обработки запросов вместе вызова requests
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

def log(object, alert: str = False, http_type: str = 'request'):
    from pathlib import Path
    import os

    path = 'logs'
    log = '{}\n{}\r\n{}\r\n\r\n{}'

    # Проверяем наличие директорий:
    if not Path(path).is_dir():
        os.mkdir(path)
    
    # Создаем папку с логами под текущую сессию работы инструмента:
    folder_name = DATETIME
    if not Path(f'{path}/{folder_name}').is_dir():
        os.mkdir(f'{path}/{folder_name}')

    if http_type == 'request':
        log = log.format(
            '-----------REQUEST-----------',
            object.method + ' ' + object.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in object.headers.items()),
            object.body,
        )
    elif http_type == 'response':
        log = log.format(
            '-----------RESPONSE-----------',
            str(object.status_code) + ' ' + object.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in object.headers.items()),
            object.content.decode(),
        )
    with open(f'{path}/{folder_name}/alerts.log' if alert else f'{path}/{folder_name}/traffic.log', 'a') as log_file:
        log_file.write(f'{log}\n')

def check_csrf_presense(html_tags):
    """

    Проверяет наличие csrf в названиях тегов
    """
    html_tags = str(html_tags).replace('[', '').replace(']', '').replace('<', '').replace('>', '').replace('/', '').replace('"', '').replace("'", '').split(', ')
    for tag in html_tags:
        name_value = tag.split('name=')[1].split(' ')[0]
        if 'csrf' in name_value:
            csrf_token = tag.split('value=')[1].split(' ')[0]
            return {'name': name_value, 'value': csrf_token}
    return {}

if __name__ == '__main__':
    pass
