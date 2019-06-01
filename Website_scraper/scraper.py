import os
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import petl as etl
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

CURRENT_PATH = os.getcwd()
DOWNLOAD_DIR = os.path.join(CURRENT_PATH, 'downloads')

URL = "http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases"

parsed_uri = urlparse(URL)
hostname = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html5lib')

pests_list = []  # a list to store quotes
table = soup.find('ul', attrs={'class': 'flex-container'})


class PageDownloader:
    def __init__(self, site_url):
        self.download_page_url = site_url

    def get_raw_html(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options,
                                  executable_path=CURRENT_PATH + '/driver/chromedriver.exe')
        print(self.download_page_url)
        driver.get(url=self.download_page_url)
        try:
            for num in range(3):
                driver.find_element_by_id('collapsible-trigger-link-' + str(num)).click()
                time.sleep(0.5)
        except NoSuchElementException:
            pass
        # time.sleep(0.5)
        values = driver.page_source
        driver.close()
        driver.quit()

        return values


def page_already_exist(file):
    exists = os.path.exists(os.path.join(DOWNLOAD_DIR, file))
    return exists


for row in table.findAll('li', attrs={'class': 'flex-item'}):
    pest = {}
    url = row.a['href']
    pest['title'] = row.text.strip()
    if 'http' in url:
        pest['url'] = url[:-1] if url[-1] == '/' else url
    else:
        pest['url'] = hostname + url
    pest['img'] = hostname + row.img['src']
    pests_list.append(pest)

extracted_data = etl.fromdicts(pests_list, header=['title', 'url', 'img'])

print(f" Total number of pests: {len(extracted_data['url'])}")

for url in extracted_data['url']:
    name = url.split('/')[-1]
    filename = f"{name}.html"
    if not page_already_exist(filename):
        downloader = PageDownloader(site_url=url)
        html = downloader.get_raw_html()
        path = os.path.join(DOWNLOAD_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)

etl.tocsv(extracted_data, 'initial_pest.csv', encoding='utf-8')
