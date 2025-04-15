import sys
sys.dont_write_bytecode = True

from modules.alanyzer import analyzer as an
from modules.spy import spy as sp
from modules.fuzzer import fuzzer as fuz
from json import load

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
    # Предварительная настройка:
    config()

    initialize_spy()  # Инициализация шпиона
    initialize_analyzer()  # Получаем пул фаззеров
    initialize_fuzzer()  # Инициализация фаззера

if __name__ == '__main__':
    run()
    
