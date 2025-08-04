import requests
from bs4 import BeautifulSoup
import re
import io
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from tables import SpimexTradingResults, Base
from xls_file_reader import read_xls_file, COLUMNS_TO_EXTRACT

BASE_URL = 'https://spimex.com'
CUTOFF_DATE = datetime(2023, 1, 1)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def get_page_soup(page_number):
    url = f"{BASE_URL}/markets/oil_products/trades/results?page=page-{page_number}"
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def get_xls_links(soup):
    links = []
    pattern = r'oil_xls_(\d{8})'
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.split("?")[0].endswith('.xls'):
            match = re.search(pattern, href)
            date_str = match.group(1)
            file_date = datetime.strptime(date_str, '%Y%m%d')
            links.append((href, file_date))
    return links


def download_xls(url):
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)


def process_xls(file_bytes, file_date):
    df = read_xls_file(file_bytes)
    rows = []

    for _, row in df.iterrows():
        result = SpimexTradingResults(
            exchange_product_id=row[COLUMNS_TO_EXTRACT["exchange_product_id"]],
            exchange_product_name=row[COLUMNS_TO_EXTRACT["exchange_product_name"]],
            oil_id=row[COLUMNS_TO_EXTRACT["exchange_product_id"]][:4],
            delivery_basis_id=row[COLUMNS_TO_EXTRACT["exchange_product_id"]][4:7],
            delivery_basis_name=row[COLUMNS_TO_EXTRACT["delivery_basis_name"]],
            delivery_type_id=row[COLUMNS_TO_EXTRACT["exchange_product_id"]][-1],
            volume=int(row[COLUMNS_TO_EXTRACT["volume"]]),
            total=int(row[COLUMNS_TO_EXTRACT["total"]]),
            count=int(row[COLUMNS_TO_EXTRACT["count"]]),
            date=file_date,
        )
        rows.append(result)

    session.add_all(rows)
    session.commit()


def main():
    page_number = 1

    while True:
        print(f"Обработка страницы {page_number}")
        soup = get_page_soup(page_number)
        links = get_xls_links(soup)

        if not links:
            break

        for link, file_date in links:
            if file_date < CUTOFF_DATE:
                return

            file_url = link if link.startswith('http') else BASE_URL + link

            print(file_url)
            file_bytes = download_xls(file_url)
            process_xls(file_bytes, file_date)

        next_page_link = soup.find('a', string='Вперед')
        if not next_page_link:
            break

        page_number += 1


if __name__ == '__main__':
    try:
        main()
    finally:
        session.close()
