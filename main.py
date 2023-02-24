import datetime
import json
import os

from Database import MongoDBWorker
from Decorators import timer
from scanners.Prisma import Prisma
from scanners.Selver import Selver
import logging


@timer
def main():
    logging.basicConfig(
        format="[%(asctime)s] [%(name)s/%(levelname)s]: %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(get_filename()),
            logging.StreamHandler()
        ]
    )

    db = MongoDBWorker("products", "matches")
    logger = logging.getLogger("main")
    logger.log(logging.INFO, 'Starting main script.')

    run_selver()
    run_prisma()

    logger.info("Merging results.")
    insert_products(db)

    logger.info("Comparing results.")
    compare_products(db)


@timer
def insert_products(dbWorker: MongoDBWorker):
    i = 0
    with open('output/prisma.json', 'r') as f:
        products = json.load(f)

    with open('output/selver.json', 'r') as f:
        products.extend(json.load(f))

    for product in products:
        i += 1
        dbWorker.insert(product, i, len(products))


@timer
def compare_products(dbWorker: MongoDBWorker):
    dbWorker.compare()


@timer
def run_selver():
    all_url = 'https://www.selver.ee/api/catalog/vue_storefront_catalog_et/product/_search?_source_exclude=sgn' \
              '&_source_include=sku&request={"query":{"bool":{"filter":{"bool":{"must":[{"terms":{"visibility":[2,3,' \
              '4]}}]}}}}}&size=100000'
    sku_url = 'https://www.selver.ee/api/catalog/vue_storefront_catalog_et/product/_search?from=0&request={"query":{' \
              '"bool":{"filter":{"bool":{"must":[{"terms":{"sku":["%ID%"]}},{"terms":{"visibility":[2,3,4]}},' \
              '{"terms":{"status":[1]}}]}}}}}&size=8&sort&_source_include=product_main_ean,product_age_restricted,' \
              'name,media_gallery.image,url_key,product_other_ean,*.is_discount,unit_price,final_*,category.name,' \
              'product_volume&_source_exclude=sgn,price_tax'

    Selver(all_url, sku_url)


@timer
def run_prisma():
    url = "https://www.prismamarket.ee/products/%ID%?main_view=1"
    Prisma(url)


def get_filename() -> str:
    date_today = datetime.date.today()
    log_num = 1
    for file in os.listdir('logs'):
        if file.startswith(str(date_today)):
            log_num += 1

    return f"logs/{date_today}-{log_num}.log"


if __name__ == "__main__":
    main()
