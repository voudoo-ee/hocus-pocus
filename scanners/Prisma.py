import asyncio
import json
import logging

from GenericParsers import category_parser, image_parser, name_parser
from scanners.Basic import BasicScanner


class Prisma:
    def __init__(self, url: str):
        p_products = []
        logger = logging.getLogger("prisma")

        logger.info("Starting first pass.")
        first_pass = asyncio.run(BasicScanner(url, range(16972, 18972)).scan())
        logger.info("Extending first pass.")
        first_pass.extend(asyncio.run(BasicScanner(url, range(18973, 20200)).scan()))

        logger.debug("Parsing products.")
        for item in first_pass:
            try:
                p_products.append(parse_product(item["data"]["entries"][0]))
            except (TypeError, IndexError):
                pass

        logger.debug("Writing results to file.")
        with open("output/prisma.json", "w") as f:
            f.write(json.dumps(p_products, indent=2))

        logger.info(f"Gathered {len(first_pass)} items")


def parse_product(product) -> dict:
    return {
        "ean": product["ean"],
        "store": "Prisma",
        "name": name_parser(product["name"]),
        "other_ean": [],
        "brand": product["subname"] if product["subname"] != "" else "N/A",
        "price": product["price"],
        "is_discount": campaign_parser(product),
        "is_age_restricted": product["contains_alcohol"],
        "weight": f"{product['quantity']} {product['comp_unit']}",
        "unit_price": product["comp_price"],
        "url": f"https://prismamarket.ee/entry/{product['ean']}",
        "category": category_parser(product["aisle"]),
        "image_url": image_parser(product, "Prisma"),
        "price_difference_float": 0.0,
        "price_difference_percentage": 0,
    }


def campaign_parser(product):
    try:
        if product["entry_ad"]:
            return True
    except KeyError:
        return False
