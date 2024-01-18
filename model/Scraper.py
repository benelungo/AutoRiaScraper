import time

import requests
from bs4 import BeautifulSoup
from model.Car import Car
from model.Parser import CarPageParser, MainPageParser
from threading import Thread, Semaphore

proxy = open("proxies.txt").read().split("\n")

num_of_threads = 8


class Scraper:
    def __init__(self, url):
        self.url = url
        self.cars = []
        self.car_urls = []
        self._page_is_last = False
        self._active_threads = 0
        self._semaphore = Semaphore(num_of_threads)

    @staticmethod
    def _make_request(url: str, proxies=None) -> BeautifulSoup:
        print("Request to url: " + url)
        response = requests.get(url, proxies=proxies)
        if response.status_code != 200:
            raise Exception("Request failed with status code: " + str(response.status_code))
        return BeautifulSoup(response.text, 'html.parser')

    def _scrap_car_page(self, url: str, proxies=None) -> None:
        # extends list of car objects
        self._active_threads += 1
        soup = self._make_request(url, proxies)
        parser = CarPageParser(soup)
        car = Car(url, *parser.get_car_info())
        self.cars.append(car)
        self._active_threads -= 1

    def _scrap_main_page(self, url, proxies=None) -> None:
        # extend list of car links
        self._active_threads += 1
        soup = self._make_request(url, proxies)
        parser = MainPageParser(soup)
        car_items = parser.get_car_items()
        if not car_items:
            self._page_is_last = True
        self.car_urls.extend([item.get("href") for item in car_items])
        print("Found car urls: " + str(len(self.car_urls)))
        self._semaphore.release()
        self._active_threads -= 1

    def _fill_car_urls(self, start_page=0, end_page=0) -> None:
        page_number = start_page
        page_size = "100"

        while not self._page_is_last and page_number <= end_page:
            self._semaphore.acquire()
            url = self.url + '&page=' + str(page_number) + '&size=' + page_size
            proxies = {'http': proxy[page_number % len(proxy)]}
            Thread(target=self._scrap_main_page, args=(url, proxies)).start()
            page_number += 1

    def _fill_cars(self) -> None:
        for i in range(len(self.car_urls)):
            self._semaphore.acquire()
            proxies = {'http': proxy[i % len(proxy)]}
            Thread(target=self._scrap_car_page, args=(self.car_urls[i], proxies)).start()

    def scrap(self, start_page, end_page) -> None:
        self._fill_car_urls(start_page, end_page)
        while self._active_threads != 0:
            time.sleep(1)
        print("Total car urls found: " + str(len(self.car_urls)))

        print("Scrapping car info...")
        self._fill_cars()
        print("Scraped cars: " + str(len(self.cars)))
        while self._active_threads != 0:
            time.sleep(1)
