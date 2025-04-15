from modules.fuzzer.process import FuzzProcess
from json import load


class Fuzzer:
    """
        Класс, анализирующий перечень фаззеров для запуска и отвечающий за их правильный запуск и передачу в них данных.
        Сущность, наследующая от этого класса, используется для проведения фаззинг-тестирования.
        Данные в сущность передаются из данных pool.json и fuzzers.json

        Задачи:
        1. Загрузка общих входных параметров и конфигураций
        2. Загрузка требуемых фаззеров и проверка правильности их настройки
        3. Запуск каждого фаззера через интерфейс FuzzProcess с правильными входными параметрами
    """
    def __init__(self):
        # Загрузка перечня необходимых к использованию фаззеров:
        self.pool: dict = load(open('data/pool.json', 'r'))
        # Загрузка всех фаззеров:
        self.fuzzers: dict = load(open('configs/fuzzers.json', 'r'))
        # Словарь, в который будут добавлены используемые фаззеры для каждого URL и вся необходимая информация о них:
        self.usable_fuzzers: dict = {}
        # Список результатов фаззинга:
        self.results: list = []

    def work(self):
        """
        Метод начала работы фаззинга. После вызова метода сущность производит 
        настройку параметров и поочередно запускает требуемые фаззеры 
        """
        # Импортируем конфиги используемых фаззеров и проверяем их:
        for endpoint in self.pool.keys():
            # Создаем пространство фаззеров очередного URL:
            self.usable_fuzzers[endpoint] = {}
            # Для каждого фаззера проверяем, есть ли он в используем пространстве фаззеров URL:
            for fuzzer in self.pool[endpoint]:
                if fuzzer['name'] not in self.usable_fuzzers[endpoint].keys():
                    # Если конфиги фаззера еще не были импортированы, импортируем их:
                    self.usable_fuzzers[endpoint][fuzzer['name']] = {
                        'details': fuzzer, 
                        'configs': self.fuzzers['all'][fuzzer['claster']][fuzzer['name']]
                    }
            # Проверяем правильность имплементации:
        
        # Запускаем фаззеры:
        for endpoint in self.usable_fuzzers.keys():
            for fuzzer in self.usable_fuzzers[endpoint].keys():
                self.results.append(FuzzProcess(self.usable_fuzzers[endpoint][fuzzer]).fuzz())


if __name__ == '__main__':
    pass
