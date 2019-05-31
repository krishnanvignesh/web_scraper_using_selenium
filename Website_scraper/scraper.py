import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import petl as etl
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

URL = "http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases"

hostname = urlparse(URL).hostname
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


for row in table.findAll('li', attrs={'class': 'flex-item'}):
    pest = {}
    url = row.a['href']
    if 'http' in url:
        pest['url'] = url
    else:
        pest['url'] = hostname + url
    pest['img'] = hostname + row.img['src']
    pest['title'] = row.text.strip()
    pests_list.append(pest)

extracted_data = etl.fromdicts(pests_list, header=['url', 'img', 'title'])

for url in extracted_data['url']:
    downloader = PageDownloader(site_url=url)
    response = downloader.get_raw_html()



etl.tocsv(extracted_data, 'new.csv', encoding='utf-8')
