from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import petl as etl
import selenium
URL = "http://www.agriculture.gov.au/pests-diseases-weeds/plant#identify-pests-diseases"

hostname = urlparse(URL).hostname
response = requests.get(URL)
soup = BeautifulSoup(response.content, 'html5lib')

pests_list = []  # a list to store quotes
table = soup.find('ul', attrs={'class': 'flex-container'})

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
    response = requests.get(URL)

etl.tocsv(extracted_data, 'new.csv', encoding='utf-8')
