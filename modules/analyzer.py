from json import load, dumps
from parsers import rules_parser
from checkers import checker

class Analyzer:
    def __init__(self):
        self.__load_endpoints()
        self.pool = {}

    def __load_endpoints(self):
        with open('data/endpoints.json', 'r') as endpoints_file:
            self.endpoints: list = load(endpoints_file)
            if not self.endpoints:
                raise ValueError('No endpoints found in endpoints.json')

    def __identify_fuzzers_pool(self, endpoint: str) -> list:
        # Процесс взаимодействия с сервером
        fuzzers_pool: list = []

        accepted_rules = checker.run(endpoint)

        with open('configs/rules.json', 'r') as rules_file:
            rules: list = load(rules_file)
        for accepted_rule in accepted_rules:
            for basic_rule in rules:
                if basic_rule['name'] == accepted_rule[0]:
                    for fuzzer in basic_rule['fuzzers']:
                        fuzzers_pool.append(
                            {
                                'claster': fuzzer['claster'], 
                                'name': fuzzer['name'],
                                'headers': '',
                                'data': '',
                                'placeholder': basic_rule['data']['placeholder'],
                                'method': '',
                                'url': ''
                            })
        return fuzzers_pool

    def identify_entry_points(self):
        for endpoint in self.endpoints:
            # Смотрим, какие фаззеры сюда применить:
            self.pool[endpoint] = self.__identify_fuzzers_pool(endpoint)
        self.save_fuzzers_pool()

    def save_fuzzers_pool(self):
        with open('data/pool.json', 'w') as pool_file:
            pool_file.write(dumps(self.pool, indent=4, sort_keys=True))


if __name__ == '__main__':
    pass
