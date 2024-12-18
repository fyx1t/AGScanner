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

    
    def pretty_print_POST(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

    def work(self, data) -> dict:
        print(data)
        print(self.get_domain())
        print(data['url'])
        print(data['data'])
        payloads = self.load_payloads(PAYLOADS_COLLECTIONS)
        if data['method'] == 'GET':
            pass
        elif data['method'] == 'POST':
            if data['placeholder'] == 'BODY':
                print(payloads)
                for payloads_collection in payloads:
                    for payload in payloads[payloads_collection]:
                        response = requests.post(f'{self.get_domain()}{data['url']}', ''.join(f"{element}={payload}&" for element in data['data'])[:-1])
                        self.pretty_print_POST(response.request)

    def insert(self, place: str, payload: str):
        pass


if __name__ == '__main__':
    pass
