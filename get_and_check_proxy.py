import requests
from bs4 import BeautifulSoup
import threading
import queue
from urllib.request import urlopen as uReq


class CheckProxy:
    def __init__(self):
        self.proxy_site = 'https://free-proxy-list.net/'
        self.q = queue.Queue()
        self.valid_proxy = []

    def get_proxy_list(self):
        """Получение списка прокси"""
        r = requests.get(self.proxy_site)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            proxy = soup.find('textarea', class_='form-control').text.split('\n\n')[1].split('\n')
            return {'status': 'OK', 'result': proxy}
        else:
            print(f'error get_proxy_list, status code = {r.status_code}')
            return {'status': 'no'}

    def add_list_to_queue(self, proxies):
        """Добавляем список прокси в очередь"""
        for p in proxies:
            self.q.put(p)

    def check_proxy_from_queue(self):
        """Проверка прокси из очереди"""
        while not self.q.empty():
            proxy = self.q.get()
            res = requests.get('https://ipinfo.io/json', proxies={'http': f'http://{proxy}',
                                                                  'https': f'https://{proxy}'})
            if res.status_code == 200:
                print(f'{proxy} +')
                self.valid_proxy.append(proxy)
            else:
                print(f'{proxy} -')

    def check_proxy_from_list(self, proxies=''):
        """Проверка прокси из очереди"""
        # for proxy in proxies:
        proxy = '103.150.40.231:8080'
        res = requests.get('https://ipinfo.io/json', proxies={'http': proxy})
        if res.status_code == 200:
            print(f'{proxy} +')
            self.valid_proxy.append(proxy)
        else:
            print(f'{proxy} -')

    def main_class(self):
        """Получение списка прокси"""
        res_get_proxy = self.get_proxy_list()
        if res_get_proxy['status'] == 'OK':
            proxies = res_get_proxy['result']
            self.check_proxy_from_list(proxies)
            # """Добавляем список прокси в очередь"""
            # self.add_list_to_queue(proxies)
            # self.check_proxy_from_queue()
            # """Создаем потоки"""
            # for _ in range(10):
            #     threading.Thread(target=self.check_proxy_from_queue).start()
        print()

    def test(self):
        self.check_proxy_from_list()


CheckProxy().test()
