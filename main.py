from modules import analyzer as an
from modules import spy as sp
from modules import fuzzer as fuz

def initialize_spy():
    print('SPY START')
    spy = sp.Spy()
    spy.conduct_reconnaissance()
    print('SPY STOP')

def initialize_analyzer():
    print('ANALYZER START')
    analyzer = an.Analyzer()
    analyzer.identify_entry_points()
    print('ANALYZER STOP')

def initialize_fuzzer():
    print('FUZZER START')
    fuzzer = fuz.Fuzzer()
    fuzzer.work()
    print('FUZZER STOP')

def run():
    initialize_spy()  # Инициализация шпиона
    initialize_analyzer()  # Получаем пул фаззеров
    initialize_fuzzer()  # Инициализация фаззера

if __name__ == '__main__':
    run()
    
