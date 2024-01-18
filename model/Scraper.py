import requests
from bs4 import BeautifulSoup
from model.Car import Car
from model.Parser import CarPageParser, MainPageParser
from multiprocessing import Pool
from threading import Thread, Semaphore

proxy = open("proxies.txt").read().split("\n")

num_of_threads = 8


class Scraper:
    def __init__(self, url):
        self.url = url
        self.cars = []
        self.car_urls = []
        self.page_is_last = False
        self.semaphore = Semaphore(num_of_threads)

    @staticmethod
    def _make_request(url: str, proxies=None) -> BeautifulSoup:
        print("Request to url: " + url)
        response = requests.get(url, proxies=proxies)
        if response.status_code != 200:
            raise Exception("Request failed with status code: " + str(response.status_code))
        return BeautifulSoup(response.text, 'html.parser')

    def _scrap_car_page(self, url: str, proxies=None) -> None:
        # extends list of car objects
        soup = self._make_request(url, proxies)
        parser = CarPageParser(soup)
        car = Car(url, *parser.get_car_info())
        self.cars.append(car)

    def _scrap_main_page(self, url, proxies=None) -> None:
        # extend list of car links
        soup = self._make_request(url, proxies)
        parser = MainPageParser(soup)
        car_items = parser.get_car_items()
        if not car_items:
            self.page_is_last = True
        self.car_urls.extend([item.get("href") for item in car_items])
        print("Found cars: " + str(len(self.car_urls)))
        self.semaphore.release()

    def scrap(self) -> list:
        page_number = 0
        page_size = "100"

        while not self.page_is_last:
            self.semaphore.acquire()
            url = self.url + '&page=' + str(page_number) + '&size=' + page_size
            proxies = {'http': proxy[page_number % len(proxy)]}
            Thread(target=self._scrap_main_page, args=(url, proxies)).start()
            page_number += 1

        for i in range(len(self.car_urls)):
            self.semaphore.acquire()
            proxies = {'http': proxy[i % len(proxy)]}
            Thread(target=self._scrap_car_page, args=(self.car_urls[i], proxies)).start()

        return self.cars
