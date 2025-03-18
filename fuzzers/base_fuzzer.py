from abc import ABC, abstractmethod
from json import load
import datetime

DATETIME = datetime.datetime.now()

class BaseFuzzer(ABC):
    @abstractmethod
    def __init__(self, url):
        super().__init__()
        self.url = url

    @abstractmethod
    def work(self, data) -> dict:
        """
        Метод, который будет выполнять фаззинг.
        Аргумент data - это данные, которые передаются на вход.
        Возвращает обработанные или измененные данные.
        """
        pass

    @abstractmethod
    def load_payloads(self, collections: list, path: str) -> dict:
        payloads = {}
        import os

        for collection in collections:
            with open(path + '/payloads/' + collection + '.txt', 'r') as file:
                payloads_temp = file.readlines()
                for id in range(len(payloads_temp)):
                    payloads_temp[id] = payloads_temp[id].replace('\n', '')
                payloads[collection] = payloads_temp
        return payloads

    def get_domain(self) -> str:
        with open('configs/main.json', 'r') as configs_file:
            return load(configs_file)['domain']
    
    def log(self, object, alert: str = False, http_type: str = 'request'):
        log = '{}\n{}\r\n{}\r\n\r\n{}'
        path = 'logs/'
        if alert:
            path += 'alerts/'
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
        with open(f'{path}{DATETIME}.log', 'a') as log_file:
            log_file.write(f'{log}\n')
    
    def check_for_alert(self):
        pass


if __name__ == '__main__':
    pass
