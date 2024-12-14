from modules import analyzer as an
from modules import spy as sp
from modules import fuzzer as fuz

def run():
    spy = sp.Spy()
    spy.conduct_reconnaissance()
    analyzer = an.Analyzer()
    analyzer.identify_entry_points()
    fuzzers_pool: dict = analyzer.identify_fuzzers_pool()
    fuzzer = fuz.Fuzzer(fuzzers_pool)
    fuzzer.fuzz()

if __name__ == '__main__':
    run()
