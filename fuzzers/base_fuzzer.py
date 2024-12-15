from abc import ABC, abstractmethod
from json import load

class BaseFuzzer(ABC):
    @abstractmethod
    def __init__(self, url):
        super().__init__()
        self.url = url

    @abstractmethod
    def work(self, data) -> dict:
        """
        Метод, который будет выполнять фаззинг.
        Аргумент data - это данные, которые передаются на вход.
        Возвращает обработанные или измененные данные.
        """
        pass

    @abstractmethod
    def load_payloads(self, collections: list, path: str) -> dict:
        payloads = {}
        import os

        for collection in collections:
            with open(path + '/payloads/' + collection + '.txt', 'r') as file:
                payloads[collection] = file.readlines()
        return payloads

    def get_domain(self) -> str:
        with open('configs/main.json', 'r') as configs_file:
            return load(configs_file)['domain']


if __name__ == '__main__':
    pass
