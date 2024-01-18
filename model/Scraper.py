import random
import requests
from bs4 import BeautifulSoup
from model.Car import Car
from model.Parser import CarPageParser, MainPageParser
from multiprocessing import Pool
from threading import Thread, Semaphore
from requests.sessions import Session
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, local

proxy = ["http://50.168.163.176:80", "http://173.245.49.58:80", "http://50.239.72.18:80", "http://50.204.219.231:80",
           "http://107.1.93.217:80", "http://50.168.163.166:80", "http://50.173.140.145:80", "http://173.245.49.50:80"]

num_of_threads = 8


class Scraper:
    def __init__(self, url):
        self.url = url
        self.car_urls = []
        self.page_is_last = False

    @staticmethod
    def _make_request(url: str, proxies=None) -> BeautifulSoup:
        print("Request to url: " + url)
        request = requests.get(url, proxies=proxies)
        if request.status_code != 200:
            raise Exception("Request failed with status code: " + str(request.status_code))
        return BeautifulSoup(request.text, 'html.parser')

    def _scrap_car_page(self, url: str, proxies=None) -> Car:
        # get car object from car page
        soup = self._make_request(url, proxies)
        parser = CarPageParser(soup)
        car = Car(url, *parser.get_car_info())
        return car

    def _scrap_main_page(self, url, proxies=None) -> None:
        # extend list of car links
        soup = self._make_request(url, proxies)
        parser = MainPageParser(soup)
        car_items = parser.get_car_items()
        if not car_items:
            self.page_is_last = True
        self.car_urls.extend([item.get("href") for item in car_items])
        print("Found cars: " + str(len(self.car_urls)))

    def scrap(self) -> list:
        page_number = 0
        page_size = "100"
        car_urls = []
        thread_local = local()

        def get_session() -> Session:
            if not hasattr(thread_local, 'session'):
                thread_local.session = requests.Session()
            return thread_local.session

        def download_link(url: str):
            session = get_session()
            with session.get(url) as response:
                print(f'Read {len(response.content)} from {url}')

        def download_all(urls: list) -> None:
            with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
                executor.map(download_link, urls)

        while not self.page_is_last:
            urls = [self.url + '&page=' + str(page_number) + '&size=' + page_size for page_number in range(page_number, page_number + num_of_threads)]
            download_all(urls)
            page_number += num_of_threads

        cars = []
        with Pool(processes=4) as pool:
            car = pool.map(self._scrap_car_page, car_urls)
            cars.append(car)

        return cars