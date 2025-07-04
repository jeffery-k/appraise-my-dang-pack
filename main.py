import datetime
import json
import math
from typing import Any

from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd
from millify import millify

from etl.evaluate import filter_trades

TEXT_KEY = "text"
ITEMS_KEY = "items"
OFFER_KEY = "offer"
REQUEST_KEY = "request"
CARDS_KEY = "cards"
CARD_ID_KEY = "card"
RARITY_KEY = "rarity"
TITLE_KEY = "title"
FLAVOR_KEY = "flavor"
SEASON_KEY = "season"
CARD_NUMBER_KEY = "cardnum"
SERIES_MAX_KEY = "seriesmax"
TRADE_COUNT_KEY = "tradeCount"
USER_KEY = "user"
UPDATED_KEY = "updated_at"
TRADE_ID_KEY = "id"
DATE_FORMAT = "%Y-%m-%d"

CARD_VALUES_FILE = "card_values.json"
PROP_VALUES_FILE = "prop_values.json"
PROP_MULTS_FILE = "prop_mults.json"
CARDS_FILE = "cards.json"
TRADES_FILE = "etl/trades.json"
METHODOLOGY_FILE = "methodology.json"

TITLE_HEADER = "Title"
FLAVOR_HEADER = "Flavor"
SEASON_HEADER = "Season"
CURRENT_VALUE_HEADER = "Current Value"
VALUE_TREND_HEADER = "Value Trend"
NUMBER_OF_TRADES_HEADER = "Number of Trades"
OFFER_HEADER = "Offer"
REQUEST_HEADER = "Request"
OFFER_VALUE_HEADER = "Offer Value"
REQUEST_VALUE_HEADER = "Request Value"
DATE_HEADER = "Date"
NET_OFFER_GAIN_HEADER = "Net Offer Gain"
LINK_HEADER = "Link"

BASE_URL = "https://dangpacks.com/"

RARITY_BLACK_NAME = "black"
RARITY_BLACK_KEY = "rarity_black"
RARITY_RAINBOW_NAME = "rainbow"
RARITY_RAINBOW_KEY = "rarity_rainbow"
RARITY_FULL_ART_NAME = "fullart"
RARITY_FULL_ART_KEY = "rarity_fullart"
RARITY_GOLD_NAME = "gold"
RARITY_GOLD_KEY = "rarity_gold"
RARITY_RED_NAME = "red"
RARITY_RED_KEY = "rarity_red"

PROP_NAME_TO_KEY = {
    RARITY_BLACK_NAME: RARITY_BLACK_KEY,
    RARITY_FULL_ART_NAME: RARITY_FULL_ART_KEY,
    RARITY_RAINBOW_NAME: RARITY_RAINBOW_KEY,
    RARITY_GOLD_NAME: RARITY_GOLD_KEY,
    RARITY_RED_NAME: RARITY_RED_KEY,
}


# converts a string representation of a timestamp into a datetime.date object
def string_to_date(string: str) -> datetime.date:
    return datetime.datetime.strptime(string.split("T")[0], DATE_FORMAT).date()


# returns the json object located at the file with name file_name
def get_data(file_name: str) -> Any:
    with open("data/" + file_name, "r") as data_file:
        return json.load(data_file)


# the View class contains methods to render all pages of the site
class View:
    def __init__(self):
        self.cards: dict[str, dict[str, Any]] = get_data(CARDS_FILE)
        self.card_values: dict[str, dict[datetime.date, int]] = {}
        self.prop_values: dict[str, dict[datetime.date, int]] = {}
        self.prop_mults: dict[str, dict[datetime.date, float]] = {}
        self.trades: list[dict[str, Any]] = filter_trades(get_data(TRADES_FILE))
        self.methodology: str = get_data(METHODOLOGY_FILE)[TEXT_KEY]
        self.card_ids: list[str] = list(self.cards.keys())
        self.card_names: dict[str: int] = {self.get_card_full_name(card): card_id for card_id, card in
                                           self.cards.items()}

        json_card_values = get_data(CARD_VALUES_FILE)
        for key, value in json_card_values.items():
            self.card_values[key] = {string_to_date(k): v for k, v in value.items()}

        json_prop_values = get_data(PROP_VALUES_FILE)
        for key, value in json_prop_values.items():
            self.prop_values[key] = {string_to_date(k): v for k, v in value.items()}

        json_prop_mults = get_data(PROP_MULTS_FILE)
        for key, value in json_prop_mults.items():
            self.prop_mults[key] = {string_to_date(k): v for k, v in value.items()}

    # render cards table view
    @st.fragment
    def cards_view(self):
        st.subheader("Cards")
        data = {
            TITLE_HEADER: [],
            FLAVOR_HEADER: [],
            SEASON_HEADER: [],
            CURRENT_VALUE_HEADER: [],
            VALUE_TREND_HEADER: [],
            NUMBER_OF_TRADES_HEADER: [],
            LINK_HEADER: [],
        }

        for card_id, card in self.cards.items():
            values = self.pad_values(self.card_values[card_id])
            data[TITLE_HEADER].append(card[TITLE_KEY])
            data[FLAVOR_HEADER].append(card[FLAVOR_KEY])
            data[SEASON_HEADER].append(card[SEASON_KEY])
            data[CURRENT_VALUE_HEADER].append(self.get_value_from_date(values))
            data[VALUE_TREND_HEADER].append(list(reversed(values.values())))
            data[NUMBER_OF_TRADES_HEADER].append(card[TRADE_COUNT_KEY])
            data[LINK_HEADER].append(f"{BASE_URL}season/{card[SEASON_KEY]}/cards/{str(card[TITLE_KEY])}")

        df = pd.DataFrame(data)
        df = df.sort_values(by=CURRENT_VALUE_HEADER, ascending=False)
        st.dataframe(
            df,
            column_config={
                TITLE_HEADER: st.column_config.TextColumn(TITLE_HEADER),
                FLAVOR_HEADER: st.column_config.TextColumn(FLAVOR_HEADER),
                SEASON_HEADER: st.column_config.NumberColumn(SEASON_HEADER),
                CURRENT_VALUE_HEADER: st.column_config.NumberColumn(CURRENT_VALUE_HEADER, format="accounting"),
                VALUE_TREND_HEADER: st.column_config.AreaChartColumn(VALUE_TREND_HEADER),
                NUMBER_OF_TRADES_HEADER: st.column_config.NumberColumn(NUMBER_OF_TRADES_HEADER),
                LINK_HEADER: st.column_config.LinkColumn(LINK_HEADER, display_text="link"),
            },
            hide_index=True
        )

    # render trades table view
    @st.fragment
    def trades_view(self):
        st.subheader("Trades")
        data = {
            OFFER_HEADER: [],
            REQUEST_HEADER: [],
            OFFER_VALUE_HEADER: [],
            REQUEST_VALUE_HEADER: [],
            NET_OFFER_GAIN_HEADER: [],
            DATE_HEADER: [],
            LINK_HEADER: [],
        }

        for trade in self.trades:
            date = datetime.datetime.strptime(trade[UPDATED_KEY].split("T")[0], DATE_FORMAT).date()
            offer_values = [self.get_card_value_from_date(card[CARD_ID_KEY], card[RARITY_KEY], date) for card in
                            trade[OFFER_KEY][CARDS_KEY]]
            request_values = [self.get_card_value_from_date(card[CARD_ID_KEY], card[RARITY_KEY], date) for card in
                              trade[REQUEST_KEY][CARDS_KEY]]
            offer_value = sum(offer_values)
            request_value = sum(request_values)
            data[OFFER_HEADER].append(
                self.card_list_to_string(
                    [card for card in trade[OFFER_KEY][CARDS_KEY]], offer_values
                )
            )
            data[REQUEST_HEADER].append(
                self.card_list_to_string(
                    [card for card in trade[REQUEST_KEY][CARDS_KEY]], request_values
                )
            )
            data[OFFER_VALUE_HEADER].append(offer_value)
            data[REQUEST_VALUE_HEADER].append(request_value)
            data[NET_OFFER_GAIN_HEADER].append(request_value - offer_value)
            data[DATE_HEADER].append(date)
            data[LINK_HEADER].append(BASE_URL + "users/-/trades/" + str(trade[TRADE_ID_KEY]))

        df = pd.DataFrame(data)
        df = df.sort_values(by=OFFER_VALUE_HEADER, ascending=False)
        st.dataframe(
            df,
            column_config={
                OFFER_HEADER: st.column_config.TextColumn(OFFER_HEADER),
                REQUEST_HEADER: st.column_config.TextColumn(REQUEST_HEADER),
                OFFER_VALUE_HEADER: st.column_config.NumberColumn(OFFER_VALUE_HEADER, format="accounting"),
                REQUEST_VALUE_HEADER: st.column_config.NumberColumn(REQUEST_VALUE_HEADER, format="accounting"),
                NET_OFFER_GAIN_HEADER: st.column_config.NumberColumn(NET_OFFER_GAIN_HEADER, format="accounting"),
                DATE_HEADER: st.column_config.DateColumn(DATE_HEADER),
                LINK_HEADER: st.column_config.LinkColumn(LINK_HEADER, display_text="link"),
            },
            hide_index=True
        )

    # render card comparison view
    @st.fragment
    def compare_view(self):
        st.subheader("Compare")
        compare_section = st.columns([4, 1, 4])[1].container()
        total_values = [0, 0]
        headers = ("Requested", "Offered")
        columns = st.columns(2)
        for i in range(2):
            column = columns[i]
            header = headers[i]
            selection = column.multiselect(header + " Cards", list(self.card_names.keys()))
            party_value_section = column.empty()

            card_values = []
            for j, card_name in enumerate(selection):
                metric_section, rarity_section = column.columns([1, 2])
                rarity = rarity_section.pills("Rarity", PROP_NAME_TO_KEY.keys(), selection_mode="single",
                                              key=f"{header}_{j}")
                value = self.get_card_value_from_date(self.card_names[card_name], rarity)
                card_values.append(value)
                metric_section.metric(selection[j], millify(value))

            party_value = sum(card_values)
            party_value_section.caption(header + " Value " + format(party_value, ","))
            total_values[i] = party_value
        if total_values[0] or total_values[1]:
            diff = total_values[1] - total_values[0]
            compare_section.metric(NET_OFFER_GAIN_HEADER, millify(diff))
            compare_section.caption(format(diff, ","))

    # render methodology page
    @st.fragment
    def methodology_view(self):
        st.subheader("Methodology")
        st.write("")
        st.text(self.methodology)

    # given a dict mapping dates to values, returns a new dict with no gaps between the quarters (3 months)
    def pad_values(self, values: dict[datetime.date, int]) -> dict[datetime.date, int]:
        padded = {}
        previous = None
        for key, value in reversed(values.items()):
            if previous is None:
                previous = key
                padded[previous] = value
                continue

            while previous + relativedelta(months=3) < key:
                previous = previous + relativedelta(months=3)
                padded[previous] = value

            previous = key
            padded[previous] = value

        return {k: v for k, v in reversed(padded.items())}

    # given a card id and rarity, returns the value of the card at the specified date
    def get_card_value_from_date(self, card_id: int | str, rarity: str | None = None,
                                 date: datetime.date | None = None) -> float:
        rarity_key = PROP_NAME_TO_KEY.get(rarity)
        rarity_values = self.prop_values.get(rarity_key)
        rarity_mults = self.prop_mults.get(rarity_key)
        card_value = self.get_value_from_date(self.card_values[str(card_id)], date)
        prop_value = self.get_value_from_date(rarity_values, date) if rarity_values else 0
        prop_mult = self.get_value_from_date(rarity_mults, date) if rarity_mults else 0
        return math.floor((card_value + prop_value) * (1 + prop_mult))

    # given a dict mapping dates to values, returns the value associated with the latest date prior to the provided date
    def get_value_from_date(self, values: dict[datetime.date, int | float],
                            date: datetime.date | None = None) -> int | float:
        if not date: return list(values.values())[0]
        for key, value in values.items():
            if key <= date:
                return value
        return list(values.values())[-1]

    # given a list of card data and their values, returns a string representation of the list
    def card_list_to_string(self, cards: list[dict[str, Any]], values: list[float]) -> str:
        string = ""
        for i in range(len(cards)):
            string += self.get_card_full_name(cards[i]) + " @" + format(values[i], ",") + ", "
        return string[:-2]

    # given card data, returns the name of the card
    def get_card_full_name(self, card: dict[str, Any]) -> str:
        return card[TITLE_KEY]


# configures and renders the website
def render():
    title = "Appraise My DangPack V2"
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)
    st.caption("*only contains cards which have been traded for other cards")
    cards_tab, trades_tab, compare_tab, methodology_tab = st.tabs(["Cards", "Trades", "Compare", "Methodology"])
    view = View()
    with cards_tab as _:
        view.cards_view()
    with trades_tab as _:
        view.trades_view()
    with compare_tab as _:
        view.compare_view()
    with methodology_tab as _:
        view.methodology_view()


if __name__ == '__main__':
    render()
