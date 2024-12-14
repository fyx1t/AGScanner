import importlib.util
import sys
import os

def import_module(path):
    """
    
    Хелпер нужен для динамической подгрузки модулей и по сути заменяет инструкцию import
    """
    # Определяем полный путь к файлу
    file_path = os.path.abspath(path)

    # Получаем имя модуля (без расширения .py)
    module_name = os.path.basename(file_path).replace(".py", "")

    # Загружаем модуль
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    fuzzer_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = fuzzer_module
    spec.loader.exec_module(fuzzer_module)

    return fuzzer_module

if __name__ == '__main__':
    pass
