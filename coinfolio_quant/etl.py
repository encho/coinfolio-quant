import os
import datetime
from pymongo import MongoClient
from etl import load_crypto_ohlc_series
from etl.load_strategy_weights import create_strategy_weights
import datalake.strategies as strategiesDB
import datalake.cryptocurrencies as cryptocurrenciesDB
# import datalake.backtest as datalake_backtest
import portfolio.backtest as backtest
from prettyprinter import pprint
import functools


def get_dates_until_today(date_string):
    date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    dates = [date]
    current_date = date

    today_at_midnight = datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)

    while current_date < today_at_midnight:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO have this as datetime object, yahoo fetching function needs to transform this into string eventually
START_DATE = "2020-01-01"

CRYPTOCURRENCIES = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD"},
    {"ticker": "ETH-USD", "base": "ETH", "quote": "USD"},
    {"ticker": "XRP-USD", "base": "XRP", "quote": "USD"},
    {"ticker": "ADA-USD", "base": "ADA", "quote": "USD"},
    # {"ticker": "BTC-EUR", "base": "BTC", "quote": "EUR"},
    # {"ticker": "ETH-EUR", "base": "ETH", "quote": "EUR"},
    # {"ticker": "XRP-EUR", "base": "XRP", "quote": "EUR"},
    # {"ticker": "ADA-EUR", "base": "ADA", "quote": "EUR"},
]


STRATEGIES = [
    {
        "ticker": "G4_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G4 Basket",
        "description": "Equally weighted portfolio of 4 main cryptocurrencies.",
    },
    {
        "ticker": "G2_EQUALLY_WEIGHTED",
        "name": "Equally Weighted G2 Basket",
        "description": "Equally weighted portfolio of 2 main cryptocurrencies.",
    }
]

# TODO eventually close connection at end of script
client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


# --------------------------------------------------------------------
# STRATEGIES
# --------------------------------------------------------------------
# clean the database collection
strategies_collection = database["strategies"]
strategies_collection.drop()
# insert the strategies infos
for strategy in STRATEGIES:
    strategies_collection.insert_one(strategy)

# --------------------------------------------------------------------
# CRYPTOCURRENCY QUOTES
# --------------------------------------------------------------------
# clean the database collection
cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
cryptocurrency_quotes_collection.drop()
# insert the quotes
for cryptocurrency in CRYPTOCURRENCIES:
    load_crypto_ohlc_series.run(
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE)


# --------------------------------------------------------------------
# STRATEGIES WEIGHTS
# --------------------------------------------------------------------
# clean the database collection
strategies_weights_collection = database["strategies_weights"]
strategies_weights_collection.drop()
# create the history of equal weighted G4/5 strategy!
dates_until_today = get_dates_until_today(START_DATE)

for strategy in STRATEGIES:
    print("creating strategy weights for strategy: " + strategy["ticker"])
    for date in dates_until_today:
        create_strategy_weights(strategies_weights_collection,
                                strategy["ticker"], date)


# --------------------------------------------------------------------
# STRATEGIES BACKTESTS
# --------------------------------------------------------------------
# create backtest for the G4 strategy...
# print("strategies backtests...")
# pprint(dates_until_today)

strategies_backtests_collection = database["strategies_backtests"]
strategies_backtests_collection.drop()


def get_backtest_data(database, strategy_ticker, currency, start_date, end_date):
    # TODO eventually into utils
    def make_row_dict(index, row):
        d = dict(row)
        d["date"] = index.to_pydatetime()
        return d

    necessary_tickers = strategiesDB.get_strategy_tickers(
        database=database, ticker=strategy_ticker,
        start_date=start_date, end_date=end_date)

    cryptocurrency_exchange_rate_tickers = list(
        map(lambda cryptocurrency: cryptocurrency + "-" + currency, necessary_tickers))

    prices_df = cryptocurrenciesDB.get_field_dataframe(
        database=database,
        tickers=cryptocurrency_exchange_rate_tickers,
        field="close",
        start_date=start_date,
        end_date=end_date
    )

    prices_list = [make_row_dict(index, row)
                   for index, row in prices_df.iterrows()]

    weights_list = strategiesDB.get_strategy_weights_series(
        database=database, ticker=strategy_ticker,
        start_date=start_date, end_date=end_date)

    # safety check: check if its same dates
    prices_dates = list(map(lambda it: it["date"], prices_list))
    weights_dates = list(map(lambda it: it["date"], weights_list))
    assert(prices_dates == weights_dates)

    backtest_data_list = []
    for (weights_item, prices_item) in zip(weights_list, prices_list):
        del prices_item["date"]
        backtest_data_item = {
            "date": weights_item["date"],
            "weights": weights_item["weights"],
            "prices": prices_item,
        }
        backtest_data_list.append(backtest_data_item)

    return backtest_data_list


def run_backtest(backtest_data, start_portfolio):
    def append_next_porfolio(portfolios_series, backtest_data_item):
        weights = backtest_data_item["weights"]
        prices = backtest_data_item["prices"]
        date = backtest_data_item["date"]
        last_portfolio = portfolios_series[-1]
        next_portfolio = backtest.create_next_portfolio(
            last_portfolio, weights, prices, date)
        portfolios_series.append(next_portfolio)
        return portfolios_series

    portfolios_series = functools.reduce(append_next_porfolio,
                                         backtest_data, [start_portfolio])
    return portfolios_series


def load_backtest_into_database(strategies_backtests_collection, strategy_ticker, start_date, end_date):

    first_backtest_date = start_date - datetime.timedelta(days=1)

    backtest_data = get_backtest_data(
        database=database,
        strategy_ticker=strategy_ticker,
        currency="USD",
        start_date=start_date,
        end_date=end_date,
    )

    portfolio_0 = {
        "strategy_ticker": strategy_ticker,
        "currency": "USD",
        "cash": 10000,
        "commission": 0.005,
        "positions": [],
        "transactions": [],
        "date": first_backtest_date,
        "positions_market_value": 0,
        "total_value": 10000,
        "commissions_paid": 0,
        "total_commissions_paid": 0,
    }

    portfolios_series = run_backtest(backtest_data, portfolio_0)

    for portfolio_item in portfolios_series:
        strategies_backtests_collection.insert_one(portfolio_item)


for strategy in STRATEGIES:
    print("creating and loading backtest for: " + strategy["ticker"])
    load_backtest_into_database(strategies_backtests_collection,
                                strategy["ticker"], dates_until_today[0], dates_until_today[-1])


client.close()
