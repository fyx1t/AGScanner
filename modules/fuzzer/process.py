from modules.fuzzer.communication import FuzzConnection
from helpers import log_http


class FuzzProcess:
    """
        Класс ответственный за работу отдельного фаззера. Для каждого фаззера
        создается сущность, наследующая этот класс. После запуска метода fuzz 
        происходит подгрузка необходимых для фаззера данных и через взаимодействие
        с вспомогательным классом FuzzConnection происходит взаимодействие с тестируемым
        сервисом

        Задачи:
        1. Подгрузка всех пэйлоудов фаззера
        2. Запуск методов из FuzzConnection с правильными входными параметрами для взаимодействия с сервисом
        3. Реагирование на итоги работы FuzzConnection
    """
    def __init__(self, fuzzer_data: str):
        self.fuzzer_data = fuzzer_data
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
        print(self.fuzzer_data['details'])
        self.standart_outputs['bad'] = self.connection_module.save_standart_outputs(self.fuzzer_data['details'])
        # Загружаем пэйлоуды фаззера:
        payloads = self.load_payloads()

        # Берем поочередно каждый набор пэйлоудов для этого фаззера:
        for payloads_collection in payloads:
            print(f'[MESSAGE] - FUZZER: {self.location} | COLLECTION: {payloads_collection} | PATH: {self.fuzzer_data["details"]["url"]}')
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
            print('-------------')
            self.connection_module.fuzz_through_payloads_combinations(payloads[payloads_collection], n, self.fuzzer_data['details'])
            print('-------------')
            self.responses[payloads_collection] = self.connection_module.responses
        
        # Когда фаззинг завершен, производим анализ всех ответов на наличие алертов:
        self.check_for_alert()

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
        """
        Метод для поиска алертов в полученных ответах от тестируемого сервиса
        """
        for key in self.responses.keys():
            for response in self.responses[key]:
                if response.status_code != 200 and response.status_code != self.standart_outputs['bad'].status_code:
                    log_http(response.request, True, 'request')
                    log_http(response, True, 'response')


if __name__ == '__main__':
    pass