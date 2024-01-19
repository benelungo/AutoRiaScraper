import re
from datetime import date

from selenium.webdriver.common.by import By


# url (строка);
# title (строка);
# price_usd (число);
# odometer (число, нужно перевести 95 тыс. в 95000 и записать как число);
# username (строка);
# phone_number (число, пример структуры: +38063……..);
# image_url (строка);
# images_count (число);
# car_number (строка);
# car_vin (строка);
# datetime_found (дата сохранения в базу);

class MainPageParser:
    """
    Class for parsing main page.
    """
    def __init__(self, soup=None):
        self.soup = soup

    def get_car_items(self) -> list:
        return self.soup.select("a.m-link-ticket")


class CarPageParser:
    """
    Class for parsing car page.

    Attributes:
        soup (BeautifulSoup): soup object

    Methods:
        get_all(self): return list of attributes

    Example:
        >>> parser = CarPageParser(soup)
        ... parser.get_all()

    Description:
    This class is used to parse car page.
    It takes soup object as an argument and returns list of attributes.

    """
    def __init__(self, soup):
        self.soup = soup

    def title(self):
        item = self.soup.select_one("h3.auto-content_title")
        if item:
            return item.get_text()

    def price_usd(self):
        item = self.soup.select_one("section.price div.price_value--additional span span")
        if item:
            return int(item.get_text()[:-1].replace(" ", ""))

    def odometer(self):
        item = self.soup.select_one("div.bold.dhide")
        if item:
            result = re.sub("[^0-9]", "", item.get_text()) or '0'
            return int(result)*1000

    def username(self):
        item = self.soup.select_one("div.seller_info_name")
        if item:
            return item.get_text().replace(" ", "")

    def phone_number(self):
        item = self.soup.select_one("a.phone")
        if item:
            number = "38" + re.sub("[^0-9]", "", item.get_text())
            return int(number)
        else:
            return '0'

    def image_url(self):
        item = self.soup.select_one('a.photo-74x56.loaded picture source')
        if item:
            return item.get('srcset').replace('s.webp', 'fx.webp')

    def images_count(self):
        return len(self.soup.select('a.photo-74x56.loaded picture source'))

    def car_number(self):
        item = self.soup.select_one("span.state-num")
        if item:
            return " ".join(item.get_text().split(" ")[:3])

    def car_vin(self):
        item = self.soup.select_one("span.label-vin")
        if item:
            return item.get_text()
        item = self.soup.select_one("span.vin-code")
        if item:
            return item.get_text()

    @staticmethod
    def datetime_found():
        return date.today().strftime("%d/%m/%Y")

    def get_car_info(self) -> list:
        return [self.title(), self.price_usd(), self.odometer(), self.username(), self.phone_number(), self.image_url(),
                self.images_count(), self.car_number(), self.car_vin(), self.datetime_found()]
