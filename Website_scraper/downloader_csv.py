#!/usr/bin/env python3
"""
In order to run this file you need to have the following requirements installed

headless browser => apt-get install chromium-chromedriver
petl==1.2.0
selenium==3.141.0

"""

import os
import sys
import time

import petl as etl
from selenium import webdriver
import concurrent.futures

from selenium.common.exceptions import NoSuchElementException

file_path = sys.argv[1]
DOWNLOAD_DIR = os.path.join(file_path, 'downloads')

BASE_URL = 'https://www.pulsiva.com/de-de/search?sSearch='


class PageDownloader:
    def __init__(self, sku):
        self.download_page_url = BASE_URL + sku

    def get_raw_html(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        try:
            driver = webdriver.Chrome(chrome_options=chrome_options,
                                      executable_path='/usr/lib/chromium-browser/chromedriver')
        except:
            driver = webdriver.Chrome(chrome_options=chrome_options,
                                      executable_path='/usr/bin/chromedriver')
        driver.get(self.download_page_url)
        try:
            [driver.find_element_by_class_name('image-gallery-right-nav').click() for _ in range(10)]  # check 10 images
        except NoSuchElementException:
            pass
        time.sleep(0.5)
        values = driver.page_source
        driver.close()
        driver.quit()
        return values


def page_already_exist(sku):
    sku = sku.replace("\n", '')
    filename = f"{sku}.html"
    exists = os.path.exists(os.path.join(DOWNLOAD_DIR, filename))
    return exists


def save_page(sku, content, sku_start_time):
    path = os.path.join(DOWNLOAD_DIR, f"{sku}.html")
    with open(path, 'w') as f:
        f.write(content)
    print(f" => Finished {sku} in {round(time.time() - sku_start_time, 2)}s")


def download_page(sku):
    sku_start_time = time.time()
    downloader = PageDownloader(sku=sku)
    html = downloader.get_raw_html()
    save_page(sku=sku, content=html, sku_start_time=sku_start_time)


def fetch_skus():
    file = etl.fromcsv(os.path.join(file_path, 'Pulsiva_Items.csv'))
    return [sku for sku in file['SKU']]


def main():
    sku_list = fetch_skus()
    threads = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for sku in sku_list:
            if page_already_exist(sku):
                # print(f"{sku} exists")
                continue
            else:
                # time.sleep(0.5)  # sleep to introduce delays for downloading the page
                # exit()
                try:
                    executor.submit(download_page, sku)
                except Exception as e:
                    print(sku, e)
        print(f'Added skus to the Pool')


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- the script took %s seconds ---" % (time.time() - start_time))
