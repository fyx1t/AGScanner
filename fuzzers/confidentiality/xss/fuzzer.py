from fuzzers.base_fuzzer import Base_Fuzzer

def run():
    fuzzer = Fuzzer()
    fuzzer.work({'status': '123'})

class Fuzzer(Base_Fuzzer):
    def work(self, data) -> dict:
        data["status"] = "fuzzed_by_example"
        return data


if __name__ == '__main__':
    pass
