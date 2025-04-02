from fuzzers.base_fuzzer import BaseFuzzer

PAYLOADS_COLLECTIONS=['basic', 'mysql']

def run(endpoint: str, data: dict):
    fuzzer = Fuzzer('', PAYLOADS_COLLECTIONS)
    fuzzer.work(data)

class Fuzzer(BaseFuzzer):
    def __init__(self, url, payloads_collections):
        super().__init__(url, payloads_collections)
        self.standart_outputs = {
            "good": None,
            "bad": None
        }

    def load_payloads(self, filenames):
        return super().load_payloads(filenames, '/'.join(__file__.split('/')[0:-1]))

if __name__ == '__main__':
    pass
