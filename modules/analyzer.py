from json import load, dumps
from parsers.fuzzers_rules import get_tokens, check_rules
from parsers.url_rules import get_url
from parsers.method_rules import get_method
from parsers.data_rules import get_data
from parsers.headers_rules import get_headers

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
        tokens: list = get_tokens()
        accepted_rules = check_rules(endpoint, tokens)
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
                                'headers': get_headers(basic_rule['data']['headers']),
                                'data': get_data(basic_rule['data']['data'], accepted_rule[1], basic_rule['data']['placeholder']),
                                'placeholder': basic_rule['data']['placeholder'],
                                'method': get_method(basic_rule['data']['method'], accepted_rule[1]),
                                'url': get_url(basic_rule['data']['url'], accepted_rule[1])
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
