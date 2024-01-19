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
    """
    Car class

    Attributes:
        url: str
        title: str
        price_usd: int
        odometer: int
        username: str
        phone_number: int
        image_url: str
        images_count: int
        car_number: str
        car_vin: str
        datetime_found: str
    Methods:
        get_all(self): return list of attributes

    Example:
        >>> car = Car(url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found)
        ... car.get_all()

    Description:
    This class is used to create objects of cars.

    """
    def __init__(self, url: str, title: str, price_usd: int,
                 odometer: int, username: str, phone_number: int, image_url: str, images_count: int,
                 car_number: str, car_vin: str, datetime_found: str):
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

    def get_all(self):
        return [self.url, self.title, self.price_usd, self.odometer, self.username, self.phone_number, self.image_url,
                self.images_count, self.car_number, self.car_vin, self.datetime_found]