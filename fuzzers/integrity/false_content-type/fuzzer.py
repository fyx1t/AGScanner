from fuzzers.base_fuzzer import BaseFuzzer

PAYLOADS_COLLECTIONS=['basic']


class Fuzzer(BaseFuzzer):
    def __init__(self):
        super().__init__(PAYLOADS_COLLECTIONS, '/'.join(__file__.split('/')[0:-1]))


if __name__ == '__main__':
    pass
