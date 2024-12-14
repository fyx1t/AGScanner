from json import load, dumps

class Analyzer:
    def __init__(self):
        self.__load_endpoints()
        self.pool = {}

    def __load_endpoints(self):
        with open('data/endpoints.json', 'r') as endpoints_file:
            self.endpoints: list = load(endpoints_file)
            if not self.endpoints:
                raise ValueError('No endpoints found in endpoints.json')

    def __identify_fuzzers_pool(self, endpoint: str):
        # Процесс взаимодействия с сервером
        pass

    def identify_entry_points(self):
        for endpoint in self.endpoints:
            # Смотрим, какие фаззеры сюда применить:
            self.__identify_fuzzers_pool(endpoint)
            self.pool[endpoint] = []
            self.pool[endpoint].append({'claster': 'confidentiality', 'name': 'sqli'})
            self.pool[endpoint].append({'claster': 'confidentiality', 'name': 'xss'})
        self.save_fuzzers_pool()

    def save_fuzzers_pool(self):
        with open('data/pool.json', 'w') as pool_file:
            pool_file.write(dumps(self.pool, indent=4, sort_keys=True))

if __name__ == '__main__':
    pass
