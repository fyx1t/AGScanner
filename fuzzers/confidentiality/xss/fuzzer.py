from fuzzers.base_fuzzer import BaseFuzzer

def run(endpoint: str, data: dict):
    fuzzer = Fuzzer('')
    fuzzer.work({'status': '123'})

class Fuzzer(BaseFuzzer):
    def __init__(self, url):
        super().__init__(url)

    def load_payloads(self, filenames):
        return super().load_payloads(filenames)

    def work(self, data) -> dict:
        data["status"] = "fuzzed_by_example"
        return data


if __name__ == '__main__':
    pass
