import time
from threading import Thread, RLock
import schedule
from model.DB import DB
from model.Scraper import MainPageScraper, CarPageScraper
from model.db_config import db_name, user, password, host

proxies = open("proxies.txt").read().split("\n")


db = DB(dbname=db_name, user=user, password=password, host=host)
db.drop_table()
db.create_table()

start = 0
end = 100000
step = 5000
page_size = "100"
cars = []
num_of_threads = 4

lock = RLock()


def page_scrap_thread(urls):
    sel = CarPageScraper()
    for car in sel.scrap(urls):
        lock.acquire()
        db.insert(car)
        lock.release()
    del sel


def main():
    threads = []
    for i in range(start, end, step):
        scraper = MainPageScraper()
        scraper.scrap("https://auto.ria.com/uk/search/?indexName=auto", i, i+step, page_size=page_size, proxies=proxies)
        urls = scraper.car_urls
        if not urls:
            print("Last page reached!")
            break

        for j in range(num_of_threads):
            print(F"Scraping from {len(urls) // num_of_threads * j} to {len(urls) // num_of_threads * (j + 1)}")
            urls_chunk = urls[len(urls) // num_of_threads * j:len(urls) // num_of_threads * (j + 1)]
            thread = Thread(target=page_scrap_thread, args=(urls_chunk,))
            thread.start()
            threads.append(thread)

        while [thread.is_alive() for thread in threads].count(True) != 0:
            time.sleep(1)

        print("Sleeping for 30 seconds...")
        time.sleep(30)
    db.dump()


schedule.every().days.at("00:00").do(main).run()

while True:
    schedule.run_pending()
    time.sleep(1)
