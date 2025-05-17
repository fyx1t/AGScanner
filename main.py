import sys
sys.dont_write_bytecode = True

from modules.alanyzer import analyzer as an
from modules.spy import spy as sp
from modules.fuzzer import fuzzer as fuz
from helpers import return_amount_of_requests
from json import load
import time

def config():
    with open('configs/main.json', 'r') as configs_file:
        configs = load(configs_file)
    
    if configs['stdout']:
        try:
            import sys
            sys.stdout = open(configs['stdout'], 'w')
        except Exception as error:
            print(f'[WARNING] - COULDNT CHANGE STDOUT TO {configs["stdout"]}.\nCONTINUE...\nREASON:\n{error}')

def initialize_spy():
    print('[SPY] - START')
    spy = sp.Spy()
    spy.conduct_reconnaissance()
    print('[SPY] - STOP')

def initialize_analyzer():
    print('[ANALYZER] - START')
    analyzer = an.Analyzer()
    analyzer.identify_entry_points()
    print('[ANALYZER] - STOP')

def initialize_fuzzer():
    print('[FUZZER] - START')
    fuzzer = fuz.Fuzzer()
    fuzzer.work()
    print('[FUZZER] - STOP')

def run():
    # Задаем начальный таймер:
    start_time = time.time()

    # Предварительная настройка:
    config()

    initialize_spy()  # Инициализация шпиона
    initialize_analyzer()  # Получаем пул фаззеров
    initialize_fuzzer()  # Инициализация фаззера

    # Задаем конечный таймер:
    end_time = time.time()

    # Выводим общее количество сделанных запросов:
    amount_of_requests = return_amount_of_requests()
    print(f'Всего было совершено {amount_of_requests} запросов')

    # Выводим время работы инструмента:
    full_work_time = end_time-start_time
    print(f'Время работы инструмента: {full_work_time}')

    # Выводим запросы в секунду:
    print(f'Количество запросов в секунду: {amount_of_requests / full_work_time}')

    import psutil
    print(f"Память: {psutil.Process().memory_info().rss / 1024 ** 2:.2f} МБ")

if __name__ == '__main__':
    run()
    
