from abc import ABC, abstractmethod

class Base_Fuzzer(ABC):
    @abstractmethod
    def work(self, data) -> dict:
        """
        Метод, который будет выполнять фаззинг.
        Аргумент data - это данные, которые передаются на вход.
        Возвращает обработанные или измененные данные.
        """
        pass


if __name__ == '__main__':
    pass
