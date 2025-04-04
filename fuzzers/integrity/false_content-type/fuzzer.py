from fuzzers.base_fuzzer import BaseFuzzer

PAYLOADS_COLLECTIONS=['basic']

def run(data: dict):
    fuzzer = Fuzzer()
    fuzzer.work(data)

class Fuzzer(BaseFuzzer):
    def __init__(self):
        super().__init__(PAYLOADS_COLLECTIONS, '/'.join(__file__.split('/')[0:-1]))

if __name__ == '__main__':
    pass
