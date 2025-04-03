from abc import ABC, abstractmethod
from helpers import make_request
from json import load
import datetime

DATETIME = datetime.datetime.now()

class BaseFuzzer(ABC):
    @abstractmethod
    def __init__(self, url, payloads_collections):
        super().__init__()
        self.url = url
        self.payloads_collections = payloads_collections

    def save_standart_outputs(self, data):
        """
        
        Функция делает предварительные запросы к серверу для сохранения стандартных ответов от него
        """
        if data['method'] == 'GET':
            pass
        elif data['method'].upper() == 'POST':
            headers = {}
            for header in data['headers'].split('; '):
                headers[header.split(': ')[0]] = header.split(': ')[1]
            print(headers)
            response = make_request('POST', f"{self.get_domain()}{data['url']}", ''.join(f"{element}=1ks92sll1lak12suod9sa12jln&" for element in data['data'])[:-1], headers=headers)
            self.standart_outputs['bad'] = response

    def work(self, data) -> dict:
        """
        Метод, который будет выполнять фаззинг.
        Аргумент data - это данные, которые передаются на вход.
        Возвращает обработанные или измененные данные.
        """
        self.save_standart_outputs(data)
        # print(f'[INFO] - FUZZING {data["url"]}')
        payloads = self.load_payloads(self.payloads_collections)
        if data['method'].upper() == 'GET':
            pass
        elif data['method'].upper() == 'POST':
            if data['placeholder'] == 'BODY':
                for payloads_collection in payloads:
                    # print(len(payloads[payloads_collection]) ** len(data['data']))

                    # Удостоверимся, что инструмент не учитывает для пэйлоудов позицию ту, где стоит знак = (что подразумевает устойчивое значение в нем, например для csrf токена)
                    n = len(data['data'])
                    for key in data['data']:
                        if '=' in key:
                            n -= 1
                    self.fuzz_through_payloads_combinations(payloads[payloads_collection], n, data)

    def fuzz_through_payloads_combinations(self, arr, n, data, current_combination=[], index=0):
        if index == n:
            headers = {}
            for header in data['headers'].split('; '):
                headers[header.split(': ')[0]] = header.split(': ')[1]
            body_data = ''
            i = 0
            for payload_key in data['data']:
                if '=' in payload_key:
                    body_data += f'{payload_key}&'
                else:
                    body_data += f'{payload_key}={current_combination[i]}&'
                    i += 1
                print(body_data)
            response = make_request('POST', f'{self.get_domain()}{data["url"]}', body_data[:-1], headers=headers)

            print('AFTER REQUEST--------------------')
            print(response.request.method)
            print(response.request)
            print(response.text)

            self.log(response.request, False, 'request')
            self.log(response, False, 'response')
            self.check_for_alert(response)
            return
        for element in arr:
            self.fuzz_through_payloads_combinations(arr, n, data, current_combination + [element], index + 1)

    @abstractmethod
    def load_payloads(self, collections: list, path: str) -> dict:
        payloads = {}

        for collection in collections:
            with open(path + '/payloads/' + collection + '.txt', 'r') as file:
                payloads_temp = file.readlines()
                for id in range(len(payloads_temp)):
                    payloads_temp[id] = payloads_temp[id].replace('\n', '')
                payloads[collection] = payloads_temp
        return payloads

    def check_for_alert(self, response):
        if response.status_code != 200 and response.status_code != self.standart_outputs['bad'].status_code:
            self.log(response.request, True, 'request')
            self.log(response, True, 'response')

    def get_domain(self) -> str:
        with open('configs/main.json', 'r') as configs_file:
            return load(configs_file)['domain']
    
    def log(self, object, alert: str = False, http_type: str = 'request'):
        from pathlib import Path
        import os

        log = '{}\n{}\r\n{}\r\n\r\n{}'
        path = 'logs'

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


if __name__ == '__main__':
    pass
