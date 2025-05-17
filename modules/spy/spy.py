from urllib.parse import urljoin, urlparse
from helpers import make_request
from bs4 import BeautifulSoup
from json import load, dump
from pathlib import Path
import requests
import os


class Spy:
    def __init__(self):
        self.visited = []
        self.start_url = load(open('configs/main.json', 'r'))['domain']
        self.to_visit = {self.start_url}

    def conduct_reconnaissance(self):
        # Создаем директорию с данными data, если она ранее не была создана (во время других сканов):
        path = 'data'
        if not Path(path).is_dir():
            os.mkdir(path)

        # Начинаем сбор ссылок:
        all_links = self.crawl_website()
        
        print("\nСобранные ссылки:")
        for link in all_links:
            print(link)

        # Сохраняем ссылки в файл endpoints.json:
        with open(path + '/endpoints.json', 'w') as endpoints_file:
            dump(all_links, endpoints_file, indent=4)


    def get_all_links(self, url):
        links = []
        try:
            response = make_request('GET', url)
            if response.history and response.status_code == 200:
                self.to_visit.add(response.url)
            elif response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    # Проверяем, что ссылка принадлежит тому же домену
                    if urlparse(full_url).netloc == urlparse(url).netloc:
                        links.append(full_url)

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе {url}: {e}")

        return links

    def crawl_website(self):
        while self.to_visit:
            current_url = self.to_visit.pop()

            if current_url not in self.visited:
                print(f"Посещаем: {current_url}")
                self.visited.append(current_url)
                links = self.get_all_links(current_url)
                self.to_visit.update(links)

         # Удаляем стартовую ссылку:
        self.visited.remove(self.start_url)

        i = 0
        for i in range(len(self.visited)):
            self.visited[i] = self.visited[i].replace(self.start_url, '')

        return self.visited

if __name__ == "__main__":
    pass
