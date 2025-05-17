from helpers import make_request, log_http, log_http_error
from requests import Request
from hashlib import md5
from random import randint
from json import load


class FuzzConnection:
    """
        Класс позволяет модулю фаззинга правильно взаимодействовать с тестируемым сервисом

        Задачи:
        1. Определение того, как правильно взаимодействовать с сервисом
        2. Фаззинг сервиса с помощью вызова helpers.make_request с правильными входными параметрами
    """
    def __init__(self):
        self.domain = load(open('configs/main.json', 'r'))['domain']
        self.responses = []

    def save_standart_outputs(self, data):
        """
        Функция делает предварительные запросы к серверу для сохранения стандартных ответов от него
        """
        headers = {}
        try:
            for header in data['headers'].split('; '):
                headers[header.split(': ')[0]] = header.split(': ')[1]
        except IndexError:
            pass
        if data['method'] == 'GET':
            response = make_request('GET', f"{self.domain}{data['url']}", headers=headers)
        elif data['method'].upper() == 'POST':
            response = make_request('POST', f"{self.domain}{data['url']}", ''.join(f"{element}={md5(f'{randint(0, 500)}'.encode()).hexdigest()}&" for element in data['data'])[:-1], headers=headers)
        return response
        
    def use_payloads_batch(self):
        pass
    
    def fuzz_through_payloads_combinations(self, arr, n, data, current_combination=[], index=0, start=True):
        """
        Метод фаззинга
        """
        current_payloads_banch = []

        if start:
            self.responses = []
        if index == n:
            i = 0
            body_data = ''
            headers = {}
            if data['headers']:
                try:
                    for header in data['headers'].split('; '):
                        headers[header.split(': ')[0]] = header.split(': ')[1]
                    for payload_key in data['data']:
                        if '=' in payload_key:
                            body_data += f'{payload_key}&'
                        else:
                            body_data += f'{payload_key}={current_combination[i]}&'
                            current_payloads_banch.append(current_combination[i])
                            i += 1
                except IndexError:
                    headers = {data['headers']: current_combination[i]}
                    current_payloads_banch.append(current_combination[i])
                    i += 1
            
            if data['placeholder'].upper() == 'URL':
                # Если фаззим в url, очищаем найденное url от аргументов и фаззим со своими:
                url = f'{self.domain}{data["url"]}'.split('?')[0] + '?'
                for payload_key in data['data']:
                    if '=' in payload_key:
                        url += f'{payload_key}&'
                    else:
                        url += f'{payload_key}={current_combination[i]}&'
                        current_payloads_banch.append(current_combination[i])
                        i += 1
                        
            if data['placeholder'].upper() == 'BODY':
                response = make_request(data['method'].upper(), f'{self.domain}{data["url"]}', body_data[:-1], headers=headers)
            elif data['placeholder'].upper() == 'HEADER':
                response = make_request(data['method'].upper(), f'{self.domain}{data["url"]}', headers=headers)
            elif data['placeholder'].upper() == 'URL':
                response = make_request(data['method'].upper(), url, headers=headers)

            # Выводим очередной запрос:
            print(f'[FUZZ] - {current_payloads_banch}')

            if response is None:
                request = Request(data['method'].upper(), f'{self.domain}{data["url"]}', headers, data=body_data[:-1] if data['placeholder'].upper() == 'BODY' else None).prepare()
                log_http(request, False, 'request')
                log_http_error()
                return

            # Логируем все запросы и ответы:
            log_http(response.request, False, 'request')
            log_http(response, False, 'response')
            # Добавляем ответ в массив, который потом будет передан в метод check_for_alert для проверки на алерты:
            self.responses.append(response)
            return
        
        for element in arr:
            self.fuzz_through_payloads_combinations(arr, n, data, current_combination + [element], index + 1, start=False)


if __name__ == '__main__':
    pass
