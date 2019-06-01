import glob
import os
import time
from bs4 import BeautifulSoup
import petl as etl

from content_parser import ContentParser

CURRENT_PATH = os.getcwd()
DOWNLOAD_DIR = os.path.join(CURRENT_PATH, 'downloads')


def get_pest_sheet():
    table = etl.fromcsv('new.csv')
    return table


def get_list():
    html_list = []
    for root, dirs, files in os.walk(DOWNLOAD_DIR):
        html_list += glob.glob(os.path.join(root, '*.html'))
    return [pest.replace(DOWNLOAD_DIR, '').replace('.html', '').replace('/', '') for pest in html_list]


def get_soup(html_path):
    with open(html_path, 'r') as file:
        content = file.read()
        html_source = content
        soup = BeautifulSoup(html_source, 'html.parser')
        # soup = BeautifulSoup(html_source, 'html.parser', from_encoding='UTF-8')
        return soup


def extract_info(pest):
    current_time = time.time()
    soup = get_soup(html_path=os.path.join(DOWNLOAD_DIR, pest + '.html'))
    parser = ContentParser(soup=soup, pest=pest)
    parser.extract()
    product_data = parser.get_product_data()
    print(f"name: {pest} time taken: {time.time() - current_time}")
    return product_data


def main():
    table_pests = get_pest_sheet()
    origin = []
    identify = []
    legal = []
    suspect = []

    for url in table_pests['url']:
        url = url[:-1] if url[-1] == '/' else url
        name = url.split('/')[-1]
        print(f'{url} - {name}')
        data = extract_info(name)
        origin.append(data.get('origin'))
        identify.append(data.get('See if you can identify the pest'))
        legal.append(data.get('Check what can legally come into Australia'))
        suspect.append(data.get('Secure any suspect specimens'))

    table_pests = etl.addcolumn(table=table_pests, field='Origin', col=origin)
    table_pests = etl.addcolumn(table=table_pests, field='See if you can identify the pest', col=identify)
    table_pests = etl.addcolumn(table=table_pests, field='Check what can legally come into Australia', col=legal)
    table_pests = etl.addcolumn(table=table_pests, field='Secure any suspect specimens', col=suspect)

    etl.tocsv(table_pests, os.path.join(os.getcwd(), 'final.csv'))


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- the script took %s seconds ---" % (time.time() - start_time))
