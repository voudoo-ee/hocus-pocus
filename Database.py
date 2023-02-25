import logging
import os

from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()


def delete(collection, ean: str = None, everything: bool = False):
    if everything:
        collection.delete_many({})
    elif ean:
        collection.delete_one({"ean": ean})


class MongoDBWorker:
    """
    MongoDBWorker class is used to connect to MongoDB and perform operations on it.

    :param collection_name: Name of the collection to connect to.
    :type collection_name: str
    """

    def __init__(self, collection_name: str, matches_collection: str):
        self.client = MongoClient(os.getenv("MONGO_CLIENT"))
        self.db = self.client["main"]
        self.collection = self.db[collection_name]
        self.matches_collection = self.db[matches_collection]
        self.logger = logging.getLogger("db")

        # delete(self.matches_collection, everything=True)

    def insert(self, product: dict, current_count: int, total_count: int):
        query = {"ean": product["ean"], "store": product["store"]}

        try:
            self.collection.find_one_and_replace(query, product, upsert=True)
            self.logger.debug(f'{product["store"]} | {(current_count / total_count) * 100:.1f}% | '
                             f'{product["name"]} | {product["price"]}')
        except errors.ServerSelectionTimeoutError:
            return

    def compare(self):
        percentages = []

        self.logger.info("Finding EAN matches.")
        parsed_eans, lonely_eans = self.find_matches()

        # Parse the matches and add them to the matches collection.
        self.logger.info(f"Updating {len(parsed_eans)} matches.")
        for item in parsed_eans:
            result = self.collection.find({"$or": [{"ean": item}, {"other-ean": item}]}, {"_id": 0})
            percentages.append(percentage_calculator(result[0]["price"], result[1]["price"]))

            # Use some data from Prisma as it's more reliable.
            if result[0]["store"] == "Selver":
                self.collection.find_one_and_update(result[0], {"$set": {"name": result[1]["name"],
                                                                         "brand": result[1]["brand"],
                                                                         "image_url": result[1]["image_url"]}})
            else:
                self.collection.find_one_and_update(result[1], {"$set": {"name": result[0]["name"],
                                                                         "brand": result[0]["brand"]}})

            self.update_item(result[0]["price"], result[1]["price"], result[0], result[1])
            self.logger.debug(f"{len(parsed_eans) - parsed_eans.index(item)} products left to update.")

        # Add the remaining lonely products to the matches collection.
        self.logger.info(f"Updating {len(lonely_eans)} lonely products.")
        for item in lonely_eans:
            result = self.collection.find_one({"$or": [{"ean": item}, {"other-ean": item}]}, {"_id": 0})
            self.matches_collection.find_one_and_update({"ean": result["ean"]}, {"$set": result}, upsert=True)
            self.logger.debug(f"{len(lonely_eans) - lonely_eans.index(item)} lonely products left to update.")

        try:
            self.logger.info(f"Done parsing products. Average {sum(percentages) / len(percentages):.1f} difference.")
        except ZeroDivisionError:
            self.logger.error("ZeroDivisionError while calculating average difference.")

    def update_item(self, price1: int, price2: int, result1: list, result2: list):
        prices = (price1, price2)
        result = (result1, result2)
        if prices[0] < prices[1]:
            # Swap the values if the first price is lower than the second.
            result = (result2, result1)
            prices = (price2, price1)

        result[1]["price_difference_float"] = float(round(prices[0] - prices[1], ndigits=1))
        result[1]["price_difference_percentage"] = percentage_calculator(prices[0], prices[1])
        self.matches_collection.find_one_and_update({"ean": result[1]["ean"]}, {"$set": result[1]}, upsert=True)

    def find_matches(self) -> tuple[list, list]:
        parsed_eans = []
        all_eans = {}
        lonely_eans = []

        for doc in self.collection.find({"category": {"$ne": "N/A"}}):
            if doc["ean"] in all_eans:
                all_eans[doc["ean"]] += 1
            else:
                all_eans[doc["ean"]] = 1

        for item in all_eans:
            if all_eans[item] >= 2:
                parsed_eans.append(item)
            else:
                lonely_eans.append(item)

        return parsed_eans, lonely_eans


def percentage_calculator(num1: int, num2: int) -> int:
    return abs(int(((num1 - num2) / ((num1 + num2) / 2)) * 100))
