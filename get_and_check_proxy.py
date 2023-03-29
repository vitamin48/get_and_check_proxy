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

    def get_proxy_list_all(self):
        """Получение полного списка прокси без группировки"""
        r = requests.get(self.proxy_site)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            proxy = soup.find('textarea', class_='form-control').text.split('\n\n')[1].split('\n')
            return {'status': 'OK', 'result': proxy}
        else:
            print(f'error get_proxy_list, status code = {r.status_code}')
            return {'status': 'no'}

    def get_proxy_list_by_htpps(self):
        """Получение полного списка прокси тольео htpps"""
        proxy_https = []
        r = requests.get(self.proxy_site)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'lxml')
            proxy = soup.find('table', class_='table table-striped table-bordered').contents[1]
            for i in proxy:
                ip = i.contents[0].text
                port = i.contents[1].text
                country = i.contents[2].text
                https = i.contents[6].text
                if https == 'yes':
                    res_proxy = ip + ':' + port
                    proxy_https.append(res_proxy)
            return {'status': 'OK', 'result': proxy_https}
        else:
            print(f'error get_proxy_list, status code = {r.status_code}')
            return {'status': 'no'}

    def add_list_to_queue(self, proxies):
        """Добавляем список прокси в очередь"""
        for p in proxies:
            self.q.put(p.split('\n')[0])

    def check_proxy_from_queue(self):
        """Проверка прокси из очереди"""
        while not self.q.empty():
            proxy = self.q.get()
            try:
                res = requests.get('https://ipinfo.io/json', proxies={'https': proxy})
                print(f'{proxy} +\n{res.text}')
                self.valid_proxy.append(proxy)
            except Exception as exp:
                print(f'{proxy} - Exception: {exp}')
        print('==============================')
        self.export_proxy_to_file()

    def export_proxy_to_file(self):
        with open('proxy_file_checked.txt', 'w+') as f:
            for i in self.valid_proxy:
                f.write(f'{i}\n')
        print("File written successfully")

    def check_proxy_from_list(self, proxies=''):
        """Проверка прокси из списка"""
        # for proxy in proxies:
        with open('proxy_file.txt', 'r') as proxy_file:
            proxy_list = proxy_file.readlines()
        for proxy in proxy_list:
            proxy = proxy.split('\n')[0]
            try:
                res = requests.get('https://ipinfo.io/json', proxies={'https': proxy}, timeout=3)
                print(f'{proxy} + \n{res.text}')
                self.valid_proxy.append(proxy)
            except Exception as exp:
                print(f'{proxy} - Exception: {exp}')

    def main_class(self):
        """Получение списка прокси"""
        # res_get_proxy = self.get_proxy_list_all()
        res_get_proxy = self.get_proxy_list_by_htpps()
        if res_get_proxy['status'] == 'OK':
            proxies = res_get_proxy['result']
            # self.check_proxy_from_list(proxies)
            """Добавляем список прокси в очередь"""
            self.add_list_to_queue(proxies)
            self.check_proxy_from_queue()
            """Создаем потоки"""
            for _ in range(10):
                threading.Thread(target=self.check_proxy_from_queue).start()
        print()

    def test(self):
        self.check_proxy_from_list()

    def get_proxy_from_file(self):
        with open('proxy_file.txt', 'r') as proxy_file:
            proxies = proxy_file.readlines()
        """Добавляем список прокси в очередь"""
        self.add_list_to_queue(proxies)
        """Создаем потоки"""
        for _ in range(10):
            threading.Thread(target=self.check_proxy_from_queue).start()


CheckProxy().get_proxy_from_file()

