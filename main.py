import datetime
import json

import streamlit as st
import pandas as pd
from tenacity import sleep_using_event

TEXT_KEY = "text"
ITEMS_KEY = "items"
OFFER_KEY = "offer"
REQUEST_KEY = "request"
CARDS_KEY = "cards"
CARD_ID_KEY = "cardId"
TITLE_KEY = "title"
FLAVOR_KEY = "flavor"
CARD_NUMBER_KEY = "cardnum"
SERIES_MAX_KEY = "seriesmax"
TRADE_COUNT_KEY = "tradeCount"
USER_KEY = "user"
UPDATED_KEY = "updated_at"
TRADE_ID_KEY = "id"
DATE_FORMAT = "%Y-%m-%d"

VALUES_FILE = "card_values.json"
CARDS_FILE = "cards.json"
TRADES_FILE = "trades.json"
METHODOLOGY_FILE = "methodology.json"

TITLE_HEADER = "Title"
FLAVOR_HEADER = "Flavor"
SERIES_NUMBER_HEADER = "Series Number"
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


class View:
    def __init__(self):
        self.cards: dict[str, dict[str, any]] = get_data(CARDS_FILE)
        self.values: dict[str, dict[datetime.date, any]] = {}
        self.trades: list[dict[str, any]] = get_data(TRADES_FILE)
        self.methodology: str = get_data(METHODOLOGY_FILE)[TEXT_KEY]
        self.card_ids: list[str] = list(self.cards.keys())
        self.card_names: dict[str: int] = {self.get_card_full_name(card): card_id for card_id, card in self.cards.items()}

        json_values = get_data(VALUES_FILE)
        for key, value in json_values.items():
            self.values[key] = {string_to_date(k): v for k, v in value.items()}

    @st.fragment
    def cards_view(self):
        st.subheader("Cards")
        data = {
            TITLE_HEADER: [],
            FLAVOR_HEADER: [],
            SERIES_NUMBER_HEADER: [],
            CURRENT_VALUE_HEADER: [],
            VALUE_TREND_HEADER: [],
            NUMBER_OF_TRADES_HEADER: [],
            LINK_HEADER: [],
        }

        for card_id, card in self.cards.items():
            values = list(self.values[card_id].values())
            data[TITLE_HEADER].append(card[TITLE_KEY])
            data[FLAVOR_HEADER].append(card[FLAVOR_KEY])
            data[SERIES_NUMBER_HEADER].append(self.get_card_series(card))
            data[CURRENT_VALUE_HEADER].append(values[-1])
            data[VALUE_TREND_HEADER].append(values)
            data[NUMBER_OF_TRADES_HEADER].append(card[TRADE_COUNT_KEY])
            data[LINK_HEADER].append(BASE_URL + "card/" + str(card_id))

        df = pd.DataFrame(data)
        st.dataframe(
            df,
            column_config={
                TITLE_HEADER: st.column_config.TextColumn(TITLE_HEADER),
                FLAVOR_HEADER: st.column_config.TextColumn(FLAVOR_HEADER),
                SERIES_NUMBER_HEADER: st.column_config.TextColumn(SERIES_NUMBER_HEADER),
                CURRENT_VALUE_HEADER: st.column_config.NumberColumn(CURRENT_VALUE_HEADER, format="accounting"),
                VALUE_TREND_HEADER: st.column_config.AreaChartColumn(VALUE_TREND_HEADER),
                NUMBER_OF_TRADES_HEADER: st.column_config.NumberColumn(NUMBER_OF_TRADES_HEADER),
                LINK_HEADER: st.column_config.LinkColumn(LINK_HEADER, display_text="link"),
            },
            hide_index=True
        )

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
            offer_values = [self.get_value_from_date(self.values[str(card[CARD_ID_KEY])], date) for card in
                    trade[OFFER_KEY][CARDS_KEY]]
            request_values = [self.get_value_from_date(self.values[str(card[CARD_ID_KEY])], date) for card in
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

    @st.fragment
    def compare_view(self):
        st.subheader("Compare")
        compare_section = st.columns(9)[4].empty()
        total_values = [0, 0]
        headers = ("Requested", "Offered")
        columns = st.columns(2)
        for i in range(2):
            column = columns[i]
            header = headers[i]
            selection = column.multiselect(header + " Cards", list(self.card_names.keys()))
            party_value_section = column.empty()

            card_values = [list(self.values[self.card_names[name]].values())[-1] for name in selection]
            for j in range(len(selection)):
                column.metric(selection[j], card_values[j])

            party_value = sum(card_values)
            party_value_section.caption(header + " Value " + format(party_value, ","))
            total_values[i] = party_value
        if total_values[0] or total_values[1]:
            compare_section.metric(NET_OFFER_GAIN_HEADER, total_values[1] - total_values[0])

    @st.fragment
    def methodology_view(self):
        st.subheader("Methodology")
        st.write("")
        st.text(self.methodology)

    def get_value_from_date(self, values: dict[datetime.date, int], date: datetime.date):
        for key, value in reversed(values.items()):
            if key <= date:
                return value
        return list(values.values())[-1]

    def card_list_to_string(self, cards: list[dict[str, any]], values: list[int]) -> str:
        string = ""
        for i in range(len(cards)):
            string += self.get_card_full_name(cards[i]) + " @" + format(values[i], ",") + ", "
        return string[:-2]

    def get_card_full_name(self, card: dict[str, any]) -> str:
        return card[TITLE_KEY] + " " + self.get_card_series(card)

    def get_card_series(self, card: dict[str, any]) -> str:
        return "(" + str(card[CARD_NUMBER_KEY]) + "/" + str(card[SERIES_MAX_KEY]) + ")"


def string_to_date(string: str) -> datetime.date:
    return datetime.datetime.strptime(string.split("T")[0], DATE_FORMAT).date()


def get_data(file_name: str) -> any:
    with open("data/" + file_name, "r") as data_file:
        return json.load(data_file)


def render():
    st.set_page_config(layout="wide")
    st.title("Appraise My DangPack")
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
