from helpers import make_request, log
from hashlib import md5
from random import randint
from json import load


class Fuzzer:
    def __init__(self):
        """
        Инициализирующий метод класса Fuzzer. Сущность, наследующая от этого класса, 
        используется для проведения фаззинг-тестирования.
        Данные в сущность передаются из данных pool.json и fuzzers.json

        Задачи:
        1. Загрузка общих входных параметров и конфигураций
        2. Загрузка требуемых фаззеров и проверка правильности их настройки
        3. Запуск каждого фаззера через интерфейс FuzzProcess с правильными входными параметрами
        """
        # Загрузка перечня необходимых к использованию фаззеров:
        self.pool: dict = load(open('data/pool.json', 'r'))
        # Загрузка всех фаззеров:
        self.fuzzers: dict = load(open('configs/fuzzers.json', 'r'))
        # Словарь, в который будут добавлены используемые фаззеры и вся необходимая информация о них:
        self.usable_fuzzers: dict = {}
        # Список результатов фаззинга:
        self.results: list = []

    def work(self):
        """
        Метод начала работы фаззинга. После вызова метода сущность производит 
        настройку параметров и поочередно запускает требуемые фаззеры 
        """
        # Импортируем конфиги используемых фаззеров и проверяем их:
        for fuzzer in [fuzzer for endpoint in self.pool.keys() for fuzzer in self.pool[endpoint] if fuzzer['name']]:
            if fuzzer['name'] not in self.usable_fuzzers.keys():
                # Если конфиги фаззера еще не были импортированы, импортируем их:
                self.usable_fuzzers[fuzzer['name']] = {
                        'details': fuzzer, 
                        'configs': self.fuzzers['all'][fuzzer['claster']][fuzzer['name']]
                    }
            # Проверяем правильность имплементации:
                
        # Запускаем фаззеры:
        for fuzzer in self.usable_fuzzers.keys():
            self.results.append(FuzzProcess(self.usable_fuzzers[fuzzer]).fuzz())


class FuzzConnection:
    def __init__(self):
        """
        Задачи:
        1. Определение того, как правильно взаимодействовать с сервисом
        2. Фаззинг сервиса с помощью вызова helpers.make_request с правильными входными параметрами
        """
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
            response = make_request('GET', f"{self.domain}{data['url']}", None, headers=headers)
        elif data['method'].upper() == 'POST':
            response = make_request('POST', f"{self.domain}{data['url']}", ''.join(f"{element}={md5(f'{randint(0, 500)}'.encode()).hexdigest()}&" for element in data['data'])[:-1], headers=headers)
            return response
        
    def use_payloads_batch(self):
        pass
    
    def fuzz_through_payloads_combinations(self, arr, n, data, current_combination=[], index=0, start=True):
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
                            i += 1
                except IndexError:
                    print(current_combination)
                    headers = {data['headers']: current_combination[i]}
                    i += 1
                        
            if data['method'].upper() == 'POST':
                response = make_request('POST', f'{self.domain}{data["url"]}', body_data[:-1], headers=headers)
                print(f'{self.domain}{data["url"]} --> {body_data[:-1]} --> {headers} --> POST')
            elif data['method'].upper() == 'GET':
                response = make_request('GET', f'{self.domain}{data["url"]}', headers=headers)
                print(f'{self.domain}{data["url"]} --> {headers} --> GET')

            # Логируем все запросы и ответы:
            log(response.request, False, 'request')
            log(response, False, 'response')
            # Добавляем ответ в массив, который потом будет передан в метод check_for_alert для проверки на алерты:
            self.responses.append(response)
            return
        
        for element in arr:
            self.fuzz_through_payloads_combinations(arr, n, data, current_combination + [element], index + 1, start=False)


class FuzzProcess:
    def __init__(self, fuzzer_data: str):
        """
        Класс ответственный за работу отдельного фаззера. Для каждого фаззера
        создается сущность, наследующая этот класс. После запуска метода fuzz 
        происходит подгрузка необходимых для фаззера данных и через взаимодействие
        с вспомогательным классом FuzzConnection происходит взаимодействие с тестируемым
        сервисом

        Задачи:
        1. Подгрузка всех пэйлоудов фаззера
        2. Распределение нагрузки фаззера ?
        3. Запуск методов из FuzzConnection с правильными входными параметрами для взаимодействия с сервисом
        4. Реагирование на итоги работы FuzzConnection
        """
        self.fuzzer_data = fuzzer_data
        print(fuzzer_data)
        self.payloads_collections = fuzzer_data['configs']['payloads']
        self.location = fuzzer_data['configs']['path']
        self.payloads_folder = fuzzer_data['configs']['payloads_folder']
        self.connection_module = FuzzConnection()
        self.standart_outputs = {
            "good": None,
            "bad": None
        }
        self.responses = {}

    def fuzz(self) -> dict:
        """
        Метод, который будет выполнять фаззинг.
        Аргумент data - это данные, которые передаются на вход.
        Возвращает обработанные или измененные данные.
        """
        # Получаем стандартный ответ от сервиса:
        self.standart_outputs['bad'] = self.connection_module.save_standart_outputs(self.fuzzer_data['details'])
        # Загружаем пэйлоуды фаззера:
        print(self.fuzzer_data['details'])
        payloads = self.load_payloads()

        # Берем поочередно каждый набор пэйлоудов для этого фаззера:
        for payloads_collection in payloads:
            # Если есть данные в словаре, то задаем длину n по количеству значений в нем (data['details'] - массив):
            if self.fuzzer_data['details']['data']:
                n = len(self.fuzzer_data['details']['data'])
                # Удостоверимся, что инструмент не учитывает для пэйлоудов позицию ту, где стоит знак = (что подразумевает устойчивое значение в нем, например для csrf токена):
                for key in self.fuzzer_data['details']['data']:
                    if '=' in key:
                        n -= 1
            else:
                # В ином случае, задаем стартовое значение в 1:
                n = 1
            # Запускаем фаззер для каждого набора с пэйлоудами с нужными настройками через интерфейс FuzzProcess:
            self.connection_module.fuzz_through_payloads_combinations(payloads[payloads_collection], n, self.fuzzer_data['details'])
            self.responses[payloads_collection] = self.connection_module.responses
        
        # Когда фаззинг завершен, производим анализ всех ответов на наличие алертов:
        self.check_for_alert()

        # Выводим информацию об окончании работы очередного фаззера:
        print(f'stoping {self.location}')

    def load_payloads(self) -> dict:
        """
        Метод загрузки пэйлоудов для конкретного фаззера
        """
        payloads = {}

        for collection in self.payloads_collections:
            with open(self.location + '/' + self.payloads_folder + '/' + collection, 'r') as file:
                payloads_temp = file.readlines()
                for id in range(len(payloads_temp)):
                    payloads_temp[id] = payloads_temp[id].replace('\n', '')
                payloads[collection] = payloads_temp
        return payloads

    def check_for_alert(self):
        for key in self.responses.keys():
            for response in self.responses[key]:
                if response.status_code != 200 and response.status_code != self.standart_outputs['bad'].status_code:
                    log(response.request, True, 'request')
                    log(response, True, 'response')


if __name__ == '__main__':
    pass
