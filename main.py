import time
from multiprocessing import Process, RLock
from threading import Thread

import schedule
from model.DB import DB
from model.Scraper import MainPageScraper, CarPageScraper
from model.db_config import db_params

proxies = open("proxies.txt").read().split("\n")

start = 0
end = 3000
step = 5
page_size = "100"
num_of_threads = 8

lock = RLock()


class Main:
    @staticmethod
    def dump_and_clear_db():
        db = DB(**db_params)
        print(db.get_all())
        db.dump()
        db.drop_table()
        db.create_table()
        del db

    @classmethod
    def page_scrap_thread(cls, urls):
        sel = CarPageScraper()
        db = DB(**db_params)
        with lock:
            for car in sel.scrap(urls):
                    db.insert(car)
        del sel
        del db

    @classmethod
    def main(cls):
        processes = []
        cls.dump_and_clear_db()

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
                process = Process(target=cls.page_scrap_thread, args=(urls_chunk,))
                process.start()
                processes.append(process)

            for process in processes:
                process.join()

            print("Sleeping for 15 seconds...")
            time.sleep(15)
        cls.insert_thread_run = False
        # insert_thread.kill()


# schedule.every().days.at("00:00").do(main).run()
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)

if __name__ == '__main__':
    Main().main()
