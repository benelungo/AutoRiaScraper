
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
    def __init__(self, soup=None):
        self.soup = soup

    def get_car_items(self) -> list:
        return self.soup.select("a.m-link-ticket")


class CarPageParser:
    def __init__(self, soup):
        self.soup = soup

    def title(self):
        return self.soup.select_one("a.ticket-item__title").get_text()

    def price_usd(self):
        return self.soup.select_one("div.ticket-item__price").get_text()

    def odometer(self):
        return self.soup.select_one("div.ticket-item__mileage").get_text()

    def username(self):
        return self.soup.select_one("div.ticket-item__user").get_text()

    def phone_number(self):
        return self.soup.select_one("div.ticket-item__phone").get_text()

    def image_url(self):
        return self.soup.select_one("div.ticket-item__image img").get("src")

    def images_count(self):
        return len(self.soup.select("div.ticket-item__image img"))

    def car_number(self):
        return self.soup.select_one("div.ticket-item__number").get_text()

    def car_vin(self):
        return self.soup.select_one("div.ticket-item__vin").get_text()

    def datetime_found(self):
        return self.soup.select_one("div.ticket-item__date").get_text()

    def get_car_info(self) -> list:
        return [self.title(), self.price_usd(), self.odometer(), self.username(), self.phone_number(), self.image_url(),
                self.images_count(), self.car_number(), self.car_vin(), self.datetime_found()]
