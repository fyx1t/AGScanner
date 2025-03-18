from modules import analyzer as an
from modules import spy as sp
from modules import fuzzer as fuz

def initialize_spy():
    try:
        spy = sp.Spy()
        spy.conduct_reconnaissance()
    except Exception as e:
        print(f"[SPY MODULE] {e}")

def initialize_analyzer():
    try:
        print('ANALYZER START')
        analyzer = an.Analyzer()
        analyzer.identify_entry_points()
        print('ANALYZER STOP')
    except Exception as e:
        print(f"[ANALYZER MODULE] {e}")

def initialize_fuzzer():
    try:
        print('FUZZER START')
        fuzzer = fuz.Fuzzer()
        fuzzer.fuzz()
        print('FUZZER STOP')
    except Exception as e:
        print(f"[FUZZER MODULE] {e}")

def run():
    initialize_spy()  # Инициализация шпиона
    initialize_analyzer()  # Получаем пул фаззеров
    initialize_fuzzer()  # Инициализация фаззера

if __name__ == '__main__':
    run()
    