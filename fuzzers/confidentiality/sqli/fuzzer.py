from fuzzers.base_fuzzer import BaseFuzzer
import requests

PAYLOADS_COLLECTIONS=['basic', 'mysql']

def run(endpoint: str, data: dict):
    fuzzer = Fuzzer('')
    fuzzer.work(data)

class Fuzzer(BaseFuzzer):
    def __init__(self, url):
        super().__init__(url)

    def load_payloads(self, filenames):
        return super().load_payloads(filenames, '/'.join(__file__.split('/')[0:-1]))

    def work(self, data) -> dict:
        payloads = self.load_payloads(PAYLOADS_COLLECTIONS)
        if data['method'] == 'GET':
            pass
        elif data['method'] == 'POST':
            if data['placeholder'] == 'BODY':
                for payloads_name in payloads:
                    requests.post(f'{self.get_domain()}{data['url']}', data['data'])

    def insert(self, place: str, payload: str):
        pass


if __name__ == '__main__':
    pass
