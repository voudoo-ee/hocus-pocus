import asyncio
import json
import logging

from GenericParsers import image_parser, category_parser, name_parser
from scanners.Basic import BasicScanner


class Selver:
    def __init__(self, all_url: str, sku_url: str):
        """
        :param all_url: The URL that will return every product.
        :param sku_url: A URL with an %ID% placeholder that will return one product.
        """

        SKUs = []
        sources = []
        p_products = []
        logger = logging.getLogger("selver")

        logger.info("Starting first pass.")
        first_pass = asyncio.run(BasicScanner(all_url).scan())
        for item in first_pass[0]["hits"]["hits"]:
            SKUs.append(item["_source"]["sku"])

        logger.info("Starting second pass.")
        second_pass = asyncio.run(BasicScanner(sku_url, id_list=SKUs).scan())

        logger.debug("Parsing products.")
        for item in second_pass:
            for product in item["hits"]["hits"]:
                sources.append(product["_source"])

        for item in sources:
            p_products.append(parse_product(item))

        logger.debug("Writing results to file.")
        with open('output/selver.json', 'w') as f:
            f.write(json.dumps(p_products, indent=2))

        logger.info(f'Gathered {len(second_pass)} items from {len(SKUs)} SKUs')


def parse_product(product) -> dict:
    other_ean = []

    try:
        if product["product_other_ean"] is None:
            other_ean = []
        elif "," in product["product_other_ean"]:
            other_ean = product["product_other_ean"].split(",")
        else:
            other_ean = [int(product["product_other_ean"])]
    except KeyError:
        pass

    return {
        "ean": int(product["product_main_ean"]),
        "name": name_parser(product["name"]),
        "other_ean": other_ean,
        "brand": "N/A",
        "store": "Selver",
        "price": float(f"{product['final_price_incl_tax']:.2f}"),
        "is_discount": product["prices"][0]["is_discount"],
        "is_age_restricted": product["product_age_restricted"],
        "weight": f"{product['product_volume']}",
        "unit_price": float(f"{product['unit_price']:.2f}"),
        "url": f"https://www.selver.ee/{product['url_key']}",
        "category": category_parser(product["category"][0]["name"]),
        "image_url": image_parser(product, "Selver"),
        "price_difference_float": 0.0,
        "price_difference_percentage": 0,
    }
