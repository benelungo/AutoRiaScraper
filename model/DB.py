import datetime
import os
import pickle
import psycopg2
from model.Car import Car


class DB:
    """
    PostgreSQL DB

    Attributes:
        dbname (str): database name
        user (str): user name
        password (str): password
        host (str): host
        table_name (str): table name

    Methods:
        get_by_url(self, url: str): get car by url
        insert(self, car: Car): insert car in the DB
        remove(self, car): remove car from the DB
        get_all(self): get all cars from the DB
        drop(self): drop table
        dump(self): dump DB
        load(self): load DB

    Example:
        >>> db = DB('dbname', 'user', 'password', 'host')
        ... car = Car(url, title, price_usd, odometer, username, phone_number, image_url, images_count, car_number, car_vin, datetime_found)
        ... db.insert(car)
        ... db.get_by_url(url)
        ... db.remove(car)

    Description:
        This is the PostgreSQL DB
        Before start using DB you must run PostgreSQL server
        You can dump and load DB via dump() and load() methods

    """
    _execute_request = '''
        CREATE TABLE IF NOT EXISTS {} (
            url TEXT PRIMARY KEY NOT NULL,
            title TEXT,
            price_usd INT,
            odometer INT,
            username TEXT,
            phone_number BIGINT,
            image_url TEXT,
            images_count INT,
            car_number TEXT,
            car_vin TEXT,
            datetime_found TEXT
        )
        '''
    _insert_request = ("INSERT INTO {} (url, title, price_usd, odometer, username, phone_number," 
                       "image_url, images_count, car_number, car_vin, datetime_found)" 
                       "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
                       "ON CONFLICT (url) DO NOTHING")
    _select_car_request = "SELECT * FROM {} WHERE url = '{}'"
    _select_all_request = "SELECT * FROM {}"
    _remove_request = "DELETE FROM cars WHERE url = '{}'"
    _drop_request = "DROP TABLE IF EXISTS {}"

    def __init__(self, dbname, user, password, host, table_name="cars"):
        self._dbname = dbname
        self._user = user
        self._password = password
        self._host = host
        self._conn = None
        self._cursor = None

        self.table_name = table_name

    def _connect_DB(self):
        self._conn = psycopg2.connect(dbname=self._dbname, user=self._user, password=self._password, host=self._host)
        self.cursor = self._conn.cursor()
        print("Connected to DB.")

    def _close_DB(self):
        self._conn.commit()
        self._conn.close()
        print("DB closed.")

    def create_table(self):
        print("Creating DB...")
        self._connect_DB()
        self.cursor.execute(self._execute_request.format(self.table_name))
        print("DB created.")
        self._close_DB()

    def drop_table(self):
        self._connect_DB()
        print("Dropping DB...")
        self.cursor.execute(self._drop_request.format(self.table_name))
        print("DB dropped.")
        self._close_DB()

    def insert(self, car: Car):
        self._connect_DB()
        print("Insert car in the DB: " + car.url)
        try:
            self.cursor.execute(self._insert_request.format(self.table_name, *car.get_all()))
        except Exception as e:
            print(e)
        self._close_DB()

    def get_all(self) -> list:
        self._connect_DB()
        print("Getting all cars from DB...")
        self.cursor.execute(self._select_all_request.format(self.table_name))
        answer = self.cursor.fetchall()
        self._close_DB()
        return answer

    def get_by_url(self, url: str) -> Car or bool:
        self._connect_DB()
        print("Getting car by url from DB: " + str(url))
        self.cursor.execute(self._select_car_request.format(self.table_name, url))
        result = self.cursor.fetchall()
        self._close_DB()
        if len(result) > 0:
            return result[0]
        print("Car not found!")
        return False

    def remove(self, car):
        print("Removing car from DB: " + str(car.id))
        self.cursor.execute(self._remove_request, (car.id,))
        self._conn.commit()

    def dump(self):
        print("Dumping DB...")
        path = f'dumps/{datetime.date.today().strftime("%d%m%Y")}.pkl'
        with open(path, 'wb+') as handle:
            pickle.dump(self.get_all(), handle)
        print("DB dumped to " + path)

    @staticmethod
    def load(date):
        with open(f'dumps/{date}.pkl', 'rb') as handle:
            return pickle.load(handle)
