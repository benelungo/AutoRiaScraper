import time

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from threading import Thread, Semaphore

from model.Car import Car
from model.Parser import CarPageParser, MainPageParser

num_of_threads = 5


class MainPageScraper:
    """
    Main page scraper

    Attributes:
        car_urls (list): list of car urls

    Methods:
        scrap(self, url, start_page, end_page, page_size='10', proxies=None)

    Example:
        >>> scraper = MainPageScraper()
        ... scraper.scrap(url, start_page, end_page, page_size='10', proxies=None)
        ... scraper.get_car_urls()

    Description:
        This is the Main page scraper
        You can get list of car urls from main page via get_car_urls() method
    """
    def __init__(self):
        self.car_urls = []
        self._threads = []
        self._page_is_last = False
        self._semaphore = Semaphore(num_of_threads)

    @staticmethod
    def _make_request(url: str, proxies=None) -> BeautifulSoup:
        print("Request to url: " + url)
        response = requests.get(url, proxies=proxies)
        if response.status_code != 200:
            raise Exception("Request failed with status code: " + str(response.status_code))
        return BeautifulSoup(response.text, 'html.parser')

    def _scrap_main_page(self, url, proxies=None) -> None:
        # extend list of car links
        soup = self._make_request(url, proxies)
        parser = MainPageParser(soup)
        car_items = parser.get_car_items()
        if not car_items:
            self._page_is_last = True
        self.car_urls.extend([item.get("href") for item in car_items])
        print("Found car urls: " + str(len(self.car_urls)))
        self._semaphore.release()

    def _fill_car_urls(self, url, start_page=0, end_page=0, page_size='10', proxies=None) -> None:
        self._threads = []
        while not self._page_is_last and end_page and start_page <= end_page:
            self._semaphore.acquire()
            search_url = url + '&page=' + str(start_page) + '&size=' + page_size
            if proxies:
                proxy = {'http': "http://" + proxies[start_page % len(proxies)]}
            else:
                proxy = None
            thread = Thread(target=self._scrap_main_page, args=(search_url, proxy))
            self._threads.append(thread)
            thread.start()
            start_page += 1

    def scrap(self, url, start_page, end_page, page_size='10', proxies=None) -> None:
        self._fill_car_urls(url, start_page, end_page-1, page_size, proxies)
        while [thread.is_alive() for thread in self._threads].count(True) != 0:
            time.sleep(1)
        print("Total car urls found: " + str(len(self.car_urls)))


class CarPageScraper:
    """
    Car page scraper

    Methods:
        scrap(self, urls)
        scrap_car_page(self, url)
        get_page_soup(self, url)

    Example:
        >>> scraper = CarPageScraper()
        ... generator = scraper.scrap(urls)
        ... car = scraper.scrap_car_page(url)
        ... soup = scraper.get_page_soup(url)

    Description:
        This class is used to scrape data from car pages.
        It uses selenium to access the car pages.
    """
    def __init__(self, proxy=None):
        self.proxy = proxy
        self.driver = self._setupDriver()
        self.first_run = True
        self._semaphore = Semaphore(num_of_threads)

    def _setupDriver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-notifications")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if self.proxy:
            options.add_argument('--proxy-server=%s' % self.proxy)

        return webdriver.Chrome(options=options)

    def _click_number_button(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'phone'))).click()

    def _click_cookie_banner(self):
        self.first_run = False
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="gdpr-notifier"]/div[1]/div[2]/label[1]'))).click()

    def get_page_soup(self, url):
        print("Scraping car url: " + url)
        self.driver.get(url)
        self.driver.implicitly_wait(30)
        # if self.first_run:
        self._click_cookie_banner()
        self.driver.implicitly_wait(3)
        try:
            self._click_number_button()
        except Exception as e:
            print("Phone number button not found: " + url)
        time.sleep(1)
        self.driver.implicitly_wait(10)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        print("Done")
        self.driver.delete_all_cookies()  # without this sometime opens page with another structure
        return soup

    def scrap_car_page(self, url: str) -> Car:
        soup = self.get_page_soup(url)
        parser = CarPageParser(soup)
        return Car(url, *parser.get_car_info())

    def scrap(self, urls) -> list:
        for url in urls:
            yield self.scrap_car_page(url)

    def __del__(self):
        self.driver.quit()
