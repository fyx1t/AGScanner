class Spy:
    def __init__(self):
        pass

    def conduct_reconnaissance(self):
        # Создаем директорию с данными data, если они ранее не была создана (в другие сканы):
        from pathlib import Path
        import os
        path = 'data'
        if not Path(path).is_dir():
            os.mkdir(path)


if __name__ == '__main__':
    pass
