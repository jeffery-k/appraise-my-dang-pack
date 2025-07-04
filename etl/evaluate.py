import datetime
import json
import math
from time import sleep
from typing import Any

import scipy

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
CASE_GRADED_KEY = "graded"
CASE_SLEEVE_KEY = "sleeve"
CASE_CENTERPIECE_KEY = "centerpiece"
RARITY_KEY = "rarity"
RARITY_GREEN_KEY = "green"
RARITY_GOLD_KEY = "gold"
RARITY_RED_KEY = "red"
RARITY_BLUE_KEY = "blue"
RARITY_PURPLE_KEY = "purple"
RARITY_SILVER_KEY = "silver"
RARITY_PINK_KEY = "pink"
RARITY_RAINBOW_KEY = "rainbow"
RARITY_BLACK_KEY = "black"
RARITY_FULLART_KEY = "fullart"
RARITY_PROMO_KEY = "promo"
RARITY_MONOCHROME_KEY = "monochrome"
STAMPED_KEY = "stamped"
STAMPED_GOLD_KEY = "gold"
STAMPED_BLUE_KEY = "blue"
STAMPED_RED_KEY = "red"
REDEEMED_KEY = "redeemed"
GRADE_OVERALL_KEY = "grade_overall"
CARD_NUM_KEY = "cardnum"
SERIES_MAX_KEY = "seriesmax"
PROP_LIST_KEY = "prop_list"

CASE_GRADED_INDEX = 0
CASE_SLEEVE_INDEX = 1
CASE_CENTERPIECE_INDEX = 2
RARITY_GREEN_INDEX = 3
RARITY_GOLD_INDEX = 4
RARITY_RED_INDEX = 5
RARITY_BLUE_INDEX = 6
RARITY_PURPLE_INDEX = 7
RARITY_SILVER_INDEX = 8
RARITY_PINK_INDEX = 9
RARITY_RAINBOW_INDEX = 10
RARITY_BLACK_INDEX = 11
RARITY_FULLART_INDEX = 12
RARITY_PROMO_INDEX = 13
RARITY_MONOCHROME_INDEX = 14
STAMPED_GOLD_INDEX = 15
STAMPED_BLUE_INDEX = 16
STAMPED_RED_INDEX = 17
UNREDEEMED_INDEX = 18
GRADE_10_INDEX = 19
GRADE_9_INDEX = 20
GRADE_8_INDEX = 21
GRADE_7_INDEX = 22
GRADE_6_INDEX = 23
GRADE_5_INDEX = 24
CARD_NUM_MIN_INDEX = 25
CARD_NUM_MAX_INDEX = 26

PROP_INDEX_TO_NAME = {
    CASE_GRADED_INDEX: "case_graded",
    CASE_SLEEVE_INDEX: "case_sleeve",
    CASE_CENTERPIECE_INDEX: "case_centerpiece",
    RARITY_GREEN_INDEX: "rarity_green",
    RARITY_GOLD_INDEX: "rarity_gold",
    RARITY_RED_INDEX: "rarity_red",
    RARITY_BLUE_INDEX: "rarity_blue",
    RARITY_PURPLE_INDEX: "rarity_purple",
    RARITY_SILVER_INDEX: "rarity_silver",
    RARITY_PINK_INDEX: "rarity_pink",
    RARITY_RAINBOW_INDEX: "rarity_rainbow",
    RARITY_BLACK_INDEX: "rarity_black",
    RARITY_FULLART_INDEX: "rarity_fullart",
    RARITY_PROMO_INDEX: "rarity_promo",
    RARITY_MONOCHROME_INDEX: "rarity_monochrome",
    STAMPED_GOLD_INDEX: "stamped_gold",
    STAMPED_BLUE_INDEX: "stamped_blue",
    STAMPED_RED_INDEX: "stamped_red",
    UNREDEEMED_INDEX: "unredeemed",
    GRADE_10_INDEX: "grade_10",
    GRADE_9_INDEX: "grade_9",
    GRADE_8_INDEX: "grade_8",
    GRADE_7_INDEX: "grade_7",
    GRADE_6_INDEX: "grade_6",
    GRADE_5_INDEX: "grade_5",
    CARD_NUM_MIN_INDEX: "card_num_min",
    CARD_NUM_MAX_INDEX: "card_num_max",
}


# writes vals as a json file with the provided name
def write_json(vals: Any, name: str):
    json_object = json.dumps(vals, indent=4)
    with open(name + ".json", "w") as out_file:
        out_file.write(json_object)


# converts a string representation of a timestamp into a datetime.date object
def string_to_date(string: str) -> datetime.date:
    return datetime.datetime.strptime(string.split("T")[0], DATE_FORMAT).date()


# given a list of trades, returns a list of the trades where at least one card was exchanged for at least one card
def filter_trades(trades: list[Any]) -> list[Any]:
    filtered = []
    for trade in trades:
        valid = len(trade[OFFER_KEY][CARDS_KEY]) and len(trade[REQUEST_KEY][CARDS_KEY])
        if valid:
            filtered.append(trade)
    return filtered


# given card data, stores a list of all the card's properties on the card and returns the list
def load_card_props(card: Any) -> list[int]:
    if card.get(PROP_LIST_KEY):
        return card[PROP_LIST_KEY]

    props = []

    case = card[CASE_KEY]
    rarity = card[RARITY_KEY]
    stamped = card[STAMPED_KEY]
    redeemed = card[REDEEMED_KEY]
    grade = card[GRADE_OVERALL_KEY]
    card_num = card[CARD_NUM_KEY]
    series_max = card[SERIES_MAX_KEY]

    if case == CASE_GRADED_KEY:
        props.append(CASE_GRADED_INDEX)
    if case == CASE_SLEEVE_KEY:
        props.append(CASE_SLEEVE_INDEX)
    if case == CASE_CENTERPIECE_KEY:
        props.append(CASE_CENTERPIECE_INDEX)

    if rarity == RARITY_GREEN_KEY:
        props.append(RARITY_GREEN_INDEX)
    if rarity == RARITY_GOLD_KEY:
        props.append(RARITY_GOLD_INDEX)
    if rarity == RARITY_RED_KEY:
        props.append(RARITY_RED_INDEX)
    if rarity == RARITY_BLUE_KEY:
        props.append(RARITY_BLUE_INDEX)
    if rarity == RARITY_PURPLE_KEY:
        props.append(RARITY_PURPLE_INDEX)
    if rarity == RARITY_SILVER_KEY:
        props.append(RARITY_SILVER_INDEX)
    if rarity == RARITY_PINK_KEY:
        props.append(RARITY_PINK_INDEX)
    if rarity == RARITY_RAINBOW_KEY:
        props.append(RARITY_RAINBOW_INDEX)
    if rarity == RARITY_BLACK_KEY:
        props.append(RARITY_BLACK_INDEX)
    if rarity == RARITY_FULLART_KEY:
        props.append(RARITY_FULLART_INDEX)
    if rarity == RARITY_PROMO_KEY:
        props.append(RARITY_PROMO_INDEX)
    if rarity == RARITY_MONOCHROME_KEY:
        props.append(RARITY_MONOCHROME_INDEX)

    if stamped == STAMPED_GOLD_KEY:
        props.append(STAMPED_GOLD_INDEX)
    if stamped == STAMPED_BLUE_KEY:
        props.append(STAMPED_BLUE_INDEX)
    if stamped == STAMPED_RED_KEY:
        props.append(STAMPED_RED_INDEX)

    if redeemed is False:
        props.append(UNREDEEMED_INDEX)

    if grade:
        if int(grade) == 10:
            props.append(GRADE_10_INDEX)
        if int(grade) == 9:
            props.append(GRADE_9_INDEX)
        if int(grade) == 8:
            props.append(GRADE_8_INDEX)
        if int(grade) == 7:
            props.append(GRADE_7_INDEX)
        if int(grade) == 6:
            props.append(GRADE_6_INDEX)
        if int(grade) == 5:
            props.append(GRADE_5_INDEX)

    if series_max > 1:
        if card_num == 1:
            props.append(CARD_NUM_MIN_INDEX)
        if card_num == series_max:
            props.append(CARD_NUM_MAX_INDEX)

    card[PROP_LIST_KEY] = props
    return props


# given the estimates of card and property values, returns the value estimate of a mint (specific copy of a card)
def get_card_value(
        values: list[float],
        locations: dict[int, int],
        prop_locations: dict[int, int],
        mult_locations: dict[int, int],
        card: Any
) -> float:
    props = load_card_props(card)
    card_location = locations[card[CARD_KEY]]
    prop_locs = [prop_locations[prop] for prop in props]
    mult_locs = [mult_locations[prop] for prop in props]

    basest_value = values[card_location]
    prop_values = [values[loc] for loc in prop_locs]
    prop_mults = [values[loc] for loc in mult_locs]

    baser_value = basest_value + sum(prop_values)
    mult_bonus = sum([mult * baser_value for mult in prop_mults])
    return baser_value + mult_bonus


# given the estimates of card and property values, returns the sum of the square errors of all trades
def find_error(
        values: list[float],
        locations: dict[int, int],
        prop_locations: dict[int, int],
        mult_locations: dict[int, int],
        trades: list[Any]
) -> float:
    error = 0
    for trade in trades:
        offer = sum([
            get_card_value(values, locations, prop_locations, mult_locations, card)
            for card in trade[OFFER_KEY][CARDS_KEY]
        ])
        request = sum([
            get_card_value(values, locations, prop_locations, mult_locations, card)
            for card in trade[REQUEST_KEY][CARDS_KEY]
        ])
        error += (offer - request) ** 2
    return error


# returns the estimates of card and property values which minimize the sum of the square errors of all trades
def minimize_errors(
        trades: list[Any],
        previous_values: dict[int, float],
        prop_previous_values: dict[int, float],
        prop_previous_mult: dict[int, float]
        # tuple[dict[card_id, card_value], dict[prop_id, prop_value], dict[prop_id, prop_mult]]
) -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    all_cards = []
    all_props = set()
    locations: dict[int, int] = {}
    prop_location: dict[int, int] = {}
    mult_location: dict[int, int] = {}
    for trade in trades:
        for party in (trade[OFFER_KEY], trade[REQUEST_KEY]):
            for card in party[CARDS_KEY]:
                all_cards.append(card)
                all_props.update(load_card_props(card))

    for i, card in enumerate(all_cards):
        card_id = card[CARD_KEY]
        if card_id not in locations:
            locations[card_id] = i

    for i, prop in enumerate(all_props):
        prop_location[prop] = len(all_cards) + i
        mult_location[prop] = len(all_cards) + len(all_props) + i

    print(f"minimizing {len(all_cards)} cards and {len(all_props)} props")

    start_values = [1] * (len(all_cards) + (2 * len(all_props)))
    for k, v in locations.items():
        if k in previous_values:
            start_values[v] = previous_values[k]
    for k, v in prop_location.items():
        if k in prop_previous_values:
            start_values[v] = prop_previous_values[k]
    for k, v in mult_location.items():
        if k in prop_previous_mult:
            start_values[v] = prop_previous_mult[k]

    results = scipy.optimize.minimize(
        lambda estimates: find_error(estimates, locations, prop_location, mult_location, trades),
        start_values,
        bounds=([(1, None)] * len(all_cards)) + ([(0, None)] * (len(all_props) * 2))
    )

    return (
        {k: results.x[v] for k, v in locations.items()},
        {k: results.x[v] for k, v in prop_location.items()},
        {k: results.x[v] for k, v in mult_location.items()},
    )


# given a date and offset, returns the first day of the quarter in which the date (with offset) took place
def get_period(date: datetime.date, offset: int = 0) -> datetime.date:
    year = date.year
    raw_month = date.month + offset
    raw_month = raw_month if raw_month <= 12 else raw_month - 12
    month = (raw_month - ((raw_month - 1) % 3))
    return datetime.date(year, month, 1)


# computes the estimates of card and property values and writes them to data files
def get_card_values():
    with open("trades.json") as trade_file:
        all_trades = filter_trades(json.load(trade_file))
        # Below will trim trade dataset for debugging
        # filter_ratio = 80
        # all_trades = [trade for index, trade in enumerate(all_trades) if (index % filter_ratio) == 0][:100]
    trades_by_period_bins = []
    for offset in (0, 1, 2):
        trades_by_period = {}
        for trade in all_trades:
            period = get_period(string_to_date(trade[UPDATED_KEY]), offset)
            if period not in trades_by_period:
                trades_by_period[period] = []
            trades_by_period[period].append(trade)
        trades_by_period = {k: trades_by_period[k] for k in sorted(trades_by_period.keys())}
        trades_by_period_bins.append(trades_by_period)

    for trade in all_trades:
        for party in (trade[OFFER_KEY], trade[REQUEST_KEY]):
            for card in party[CARDS_KEY]:
                load_card_props(card)

    previous_cards = {}
    previous_props = {}
    previous_mults = {}

    # sleep_duration = 1
    sleep_duration = 60
    # iteration_count = 9
    iteration_count = 33
    master_set = []
    for iteration in range(1, iteration_count + 1):
        print("STARTING ITERATION " + str(iteration))

        all_card_values = {}
        all_prop_values = {}
        all_prop_mults = {}
        offset = iteration % 3
        trade_bin = trades_by_period_bins[offset]
        all_trades = trade_bin.items() if iteration % 2 else reversed(trade_bin.items())

        for period, trades in all_trades:
            print("optimizing " + str(len(trades)) + " trades in period " + str(period))
            card_values, prop_values, prop_mults = minimize_errors(trades, previous_cards, previous_props,
                                                                   previous_mults)

            for card, value in card_values.items():
                previous_cards[card] = value
                if card not in all_card_values:
                    all_card_values[card] = {}
                all_card_values[card][str(period)] = math.floor(value * 10000)

            for prop, value in prop_values.items():
                previous_props[prop] = value
                if prop not in all_prop_values:
                    all_prop_values[prop] = {}
                all_prop_values[prop][str(period)] = math.floor(value * 10000)

            for prop, mult in prop_mults.items():
                previous_mults[prop] = mult
                if prop not in all_prop_mults:
                    all_prop_mults[prop] = {}
                all_prop_mults[prop][str(period)] = round(mult, 5)

            sleep(sleep_duration)

        all_card_values = {k: all_card_values[k] for k in
                           sorted(all_card_values.keys(), key=lambda x: -len(all_card_values[x]))}
        write_json(all_card_values, "values/card_values_" + str(iteration))

        all_card_values = {k: all_card_values[k] for k in
                           sorted(all_card_values.keys(), key=lambda x: -list(all_card_values[x].values())[-1])}
        write_json(all_card_values, "values/card_values_by_cost_" + str(iteration))

        all_prop_values = {PROP_INDEX_TO_NAME[k]: all_prop_values[k] for k in sorted(all_prop_values.keys())}
        write_json(all_prop_values, "values/prop_values_" + str(iteration))

        all_prop_mults = {PROP_INDEX_TO_NAME[k]: all_prop_mults[k] for k in sorted(all_prop_mults.keys())}
        write_json(all_prop_mults, "values/prop_mults_" + str(iteration))

        if iteration > (iteration_count - 3):
            master_entry = {
                "card_values": all_card_values,
                "prop_values": all_prop_values,
                "prop_mults": all_prop_mults,
            }
            master_set.append(master_entry)

        sleep(sleep_duration * 3)

    master_dict = {
        "card_values": {},
        "prop_values": {},
        "prop_mults": {},
    }
    for entry in master_set:
        for entry_type, entry_dict in entry.items():
            for key, values in entry_dict.items():
                if key not in master_dict[entry_type]:
                    master_dict[entry_type][key] = {}
                for time, value in values.items():
                    master_dict[entry_type][key][time] = value
    for entry_type, entry_dict in master_dict.items():
        for key, values in list(entry_dict.items()):
            entry_dict[key] = {k: values[k] for k in sorted(values.keys(), reverse=True)}

    all_card_values = master_dict["card_values"]
    all_prop_values = master_dict["prop_values"]
    all_prop_mults = master_dict["prop_mults"]

    all_card_values = {k: all_card_values[k] for k in
                       sorted(all_card_values.keys(), key=lambda x: -len(all_card_values[x]))}
    write_json(all_card_values, "values/master_card_values")

    all_card_values = {k: all_card_values[k] for k in
                       sorted(all_card_values.keys(), key=lambda x: -list(all_card_values[x].values())[-1])}
    write_json(all_card_values, "values/master_card_values_by_cost")

    all_prop_values = {k: all_prop_values[k] for k in sorted(all_prop_values.keys())}
    write_json(all_prop_values, "values/master_prop_values")

    all_prop_mults = {k: all_prop_mults[k] for k in sorted(all_prop_mults.keys())}
    write_json(all_prop_mults, "values/master_prop_mults")


# note, this script takes an obscene amount of time to run
if __name__ == '__main__':
    get_card_values()
