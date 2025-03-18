from fuzzers.base_fuzzer import BaseFuzzer
import requests

PAYLOADS_COLLECTIONS=['basic', 'mysql']

def run(endpoint: str, data: dict):
    fuzzer = Fuzzer('')
    fuzzer.work(data)

class Fuzzer(BaseFuzzer):
    def __init__(self, url):
        super().__init__(url)
        self.standart_outputs = {
            "good": None,
            "bad": None
        }

    def load_payloads(self, filenames):
        return super().load_payloads(filenames, '/'.join(__file__.split('/')[0:-1]))
    
    def pretty_print_POST(self, req):
        self.log('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------REQUEST-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))
    
    def save_standart_outputs(self, data):
        """
        
        Функция делает предварительные запросы к серверу для сохранения стандартных ответов от него
        """
        if data['method'] == 'GET':
            pass
        elif data['method'].upper() == 'POST':
            headers = {}
            for header in data['headers'].split('; '):
                headers[header.split(': ')[0]] = header.split(': ')[1]
            response = requests.post(f"{self.get_domain()}{data['url']}", ''.join(f"{element}=1ks92sll1lak12suod9sa12jln&" for element in data['data'])[:-1], headers=headers)
            self.standart_outputs['bad'] = response

    def check_for_alert(self, response):
        if response.status_code != 200 and response.status_code != self.standart_outputs['bad'].status_code:
            self.log(response, True, 'response')

    def fuzz_through_payloads_combinations(self, arr, n, data, current_combination=[], index=0):
        if index == n:
            headers = {}
            for header in data['headers'].split('; '):
                headers[header.split(': ')[0]] = header.split(': ')[1]
            body_data = ''
            i = 0
            for payload_key in data['data']:
                body_data += f'{payload_key}={current_combination[i]}&'
                i += 1
            response = requests.post(f"{self.get_domain()}{data['url']}", body_data[:-1], headers=headers)
            self.log(response.request, False, 'request')
            self.log(response, False, 'response')
            self.check_for_alert(response)
            return
        for element in arr:
            self.fuzz_through_payloads_combinations(arr, n, data, current_combination + [element], index + 1)

    def work(self, data) -> dict:
        self.save_standart_outputs(data)
        # print(f'[INFO] - FUZZING {data["url"]}')
        payloads = self.load_payloads(PAYLOADS_COLLECTIONS)
        if data['method'].upper() == 'GET':
            pass
        elif data['method'].upper() == 'POST':
            if data['placeholder'] == 'BODY':
                for payloads_collection in payloads:
                    # print(len(payloads[payloads_collection]) ** len(data['data']))
                    self.fuzz_through_payloads_combinations(payloads[payloads_collection], len(data['data']), data)


if __name__ == '__main__':
    pass
