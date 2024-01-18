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

class Car:
    def __init__(self, id_: int, url: str, title: str, price_usd: int,
                 odometer: int, username: str, phone_number: int, image_url: str, images_count: int,
                 car_number: str, car_vin: str, datetime_found: str):
        self.id = id_
        self.url = url
        self.title = title
        self.price_usd = price_usd
        self.odometer = odometer
        self.username = username
        self.phone_number = phone_number
        self.image_url = image_url
        self.images_count = images_count
        self.car_number = car_number
        self.car_vin = car_vin
        self.datetime_found = datetime_found

