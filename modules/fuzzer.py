from json import load
from helpers import import_module
from fuzzers.base_fuzzer import Base_Fuzzer

class Fuzzer:
    def __init__(self):
        self.__load_pool()
        self.__load_fuzzers()
        self.usable_fuzzers = {}
    
    def __load_pool(self):
        with open('data/pool.json', 'r') as pool_file:
            self.pool: dict = load(pool_file)

    def __load_fuzzers(self):
        with open('configs/fuzzers.json', 'r') as fuzzers_file:
            self.fuzzers: dict = load(fuzzers_file)

    def __import_fuzzer(self, endpoint_fuzzer: str):
        return import_module(f"{self.fuzzers['all'][endpoint_fuzzer['claster']][endpoint_fuzzer['name']]['path']}/{self.fuzzers['all'][endpoint_fuzzer['claster']][endpoint_fuzzer['name']]['filename']}")

    def check_fuzzer_implementation(self, module):
        if hasattr(module, 'Fuzzer'):
            fuzzer_class = getattr(module, 'Fuzzer')
            if issubclass(fuzzer_class, Base_Fuzzer):
                if hasattr(module, 'run'):
                    if hasattr(fuzzer_class, 'work') and callable(getattr(fuzzer_class, 'work')):
                        return True, ''
                    return False, f'Основной класс фаззера {module} не имеет установочной функции work'
                return False, f'Фаззер {module} не имеет установочной функции run'
            return False, f'Основной класс фаззера {module} не наследуется от базового класса'
        return False, f'Фаззер {module} не имеет класса Fuzzer'

    def fuzz(self):
        for endpoint in self.pool.keys():
            for fuzzer in self.pool[endpoint]:
                if fuzzer['name'] not in self.usable_fuzzers.keys():
                    # Если фаззер еще не был импортирован, импортируем:
                    fuzzer_module = self.__import_fuzzer(fuzzer)
                    self.usable_fuzzers[fuzzer['name']] = fuzzer_module
                # Проверяем правильность имплементации и запускаем фаззер с нужными параметрами:
                implementation_state, state_message = self.check_fuzzer_implementation(self.usable_fuzzers[fuzzer['name']])
                if implementation_state:
                    results = self.usable_fuzzers[fuzzer['name']].run()
                else:
                    raise AttributeError(state_message)

if __name__ == '__main__':
    pass
