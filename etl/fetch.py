import datetime
import json
from time import sleep
from typing import Any

import requests

URL = "https://tvoee3zqq5.execute-api.us-east-1.amazonaws.com/v2/trades"
BIN_SIZE = 50
ITEMS_KEY = "items"
OFFER_KEY = "offer"
REQUEST_KEY = "request"
CARDS_KEY = "cards"
CARD_KEY = "card"
CARD_ID_KEY = "cardId"
OWNER_KEY = "owner"
OWNER_ID_KEY = "owner_id"
SEASON_KEY = "season"
TRADE_COUNT_KEY = "tradeCount"
ALTERNATES_KEY = "alternates"
DIFFS_KEY = "diffs"
ALTERNATES_COUNT_KEY = "alternatesCount"
USER_KEY = "user"
UPDATED_KEY = "updated_at"
DATE_FORMAT = "%Y-%m-%d"

CASE_KEY = "case"
RARITY_KEY = "rarity"
STAMPED_KEY = "stamped"


# writes vals as a json file with the provided name
def write_json(vals: Any, name: str):
    json_object = json.dumps(vals, indent=4)
    with open(name + ".json", "w") as out_file:
        out_file.write(json_object)


# converts a string representation of a timestamp into a datetime.date object
def string_to_date(string: str) -> datetime.date:
    return datetime.datetime.strptime(string.split("T")[0], DATE_FORMAT).date()


# given an offset and limit, returns the prefix string of the trade query
def get_limit_query(offset: int, limit: int) -> str:
    return "?offset=" + str(offset) + "&limit=" + str(limit) + "&status=accepted"


# queries all the trades available via the DangPacks api and writes them to a data file
def get_trades():
    trades = []
    offset = 0
    retry = 0
    while True:
        url = URL + get_limit_query(offset, BIN_SIZE)
        error = None
        response = None
        try:
            response = requests.get(url, timeout=60)
        except Exception as e:
            error = e

        if error or response.status_code != 200:
            retry += 1
            print(str(error if error else response))
            print(f"hang: {retry}")
            if retry > 3:
                break
            else:
                continue
        elif len(response.json()[ITEMS_KEY]) == 0:
            print("all done :)")
            break
        else:
            retry = 0

        trades += response.json()[ITEMS_KEY]
        print("fetched " + str(offset) + " - " + str(offset + BIN_SIZE))
        offset += BIN_SIZE
        sleep(0.5)
        if offset % (BIN_SIZE * 10) == 0:
            print("long wait...")
            sleep(20)

    write_json(trades, "trades")


# finds all the unique cards among trades and writes them to a data file
def get_cards():
    with open("trades.json") as trade_file:
        all_trades = json.load(trade_file)
    all_cards = {}
    for trade in all_trades:
        for party in (trade[OFFER_KEY], trade[REQUEST_KEY]):
            for card in party[CARDS_KEY]:
                card_id = card[CARD_KEY]
                if card_id not in all_cards:
                    all_cards[card_id] = card
                    all_cards[card_id][TRADE_COUNT_KEY] = 0
                all_cards[card_id][TRADE_COUNT_KEY] += 1

    all_cards = {k: all_cards[k] for k in sorted(all_cards.keys(), key=lambda k: -all_cards[k][TRADE_COUNT_KEY])}
    write_json(all_cards, "cards")


# finds all the unique variations between cards and writes them to data files
# this method is primarily for data exploration and modelling which card properties are relevant
def get_variations():
    with open("trades.json") as trade_file:
        all_trades = json.load(trade_file)
    all_cards = {}
    for trade in all_trades:
        for party in (trade[OFFER_KEY], trade[REQUEST_KEY]):
            for card in party[CARDS_KEY]:
                card_id = card[CARD_ID_KEY]
                if card_id not in all_cards:
                    all_cards[card_id] = card
                    all_cards[card_id][TRADE_COUNT_KEY] = 0
                all_cards[card_id][TRADE_COUNT_KEY] += 1

    all_variations = {}
    for card in all_cards.values():
        for key, value in card.items():
            if key not in all_variations:
                all_variations[key] = []
            if value not in all_variations[key]:
                all_variations[key].append(value)
    for key in all_variations.keys():
        if len(all_variations[key]) > 100:
            all_variations[key] = "...a lot"
    write_json(all_variations, "variations")

    rarities = {
        RARITY_KEY: {},
        CASE_KEY: {},
        STAMPED_KEY: {},
    }
    for card in all_cards.values():
        for key in rarities.keys():
            rarity = card[key]
            if rarity not in rarities[key]:
                rarities[key][rarity] = []
            rarities[key][rarity].append(card[CARD_ID_KEY])
    write_json(rarities, "rarities")


if __name__ == '__main__':
    get_trades()
    get_cards()
    get_variations()
