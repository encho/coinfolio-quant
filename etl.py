import os
import datetime
from pymongo import MongoClient
from coinfolio_quant.etl import load_crypto_ohlc_series
from coinfolio_quant.etl.load_strategy_weights import create_strategy_weights
import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrenciesDB
import coinfolio_quant.portfolio.backtest as backtest
from prettyprinter import pprint
import functools


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d")


def get_dates_for_period(start_date_string, end_date_string):
    start_date = parse_date(start_date_string)
    dates = [start_date]
    current_date = start_date

    end_date = parse_date(end_date_string)

    while current_date < end_date:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

# TODO have this as datetime object, yahoo fetching function needs to transform this into string eventually
# long backtest
START_DATE = "2014-09-17"  # not there for eth
END_DATE = "2022-07-22"

# short backtest
# START_DATE = "2020-01-02"
# END_DATE = "2020-12-31"


CRYPTOCURRENCIES = [
    {"ticker": "BTC-USD", "base": "BTC", "quote": "USD", "yahoo_ticker": "BTC-USD"},
    {"ticker": "XAU-USD", "base": "XAU", "quote": "USD", "yahoo_ticker": "GC=F"},
    # {"ticker": "ETH-USD", "base": "ETH", "quote": "USD", "yahoo_ticker": "ETH-USD"},
    # {"ticker": "XRP-USD", "base": "XRP", "quote": "USD", "yahoo_ticker": "XRP-USD"},
    # {"ticker": "ADA-USD", "base": "ADA", "quote": "USD", "yahoo_ticker": "ADA-USD"},
]


STRATEGIES = [
    {
        "ticker": "BITCOIN_ONLY",
        "name": "Bitcoin Long Only Strategy",
        "description": "Bitcoin Long Only Strategy Description",
        "rebalancing": "DAILY"
    },
    {
        "ticker": "CFBG1",
        "name": "Coinfolio Bitcoin & Gold Balanced Index",
        "description": "Coinfolio Bitcoin & Gold Balanced Index (Description)",
        "rebalancing": "MONTHLY"
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "name": "Gold Crypto 60-40 Basket",
        "description": "Gold & Crypto Portfolio 60/40",
        "rebalancing": "MONTHLY"
    },
    # ===============================================================================
    # {
    #     "ticker": "G4_EQUALLY_WEIGHTED",
    #     "name": "Equally Weighted G4 Basket",
    #     "description": "Equally weighted portfolio of 4 main cryptocurrencies.",
    # },
    # {
    #     "ticker": "G2_EQUALLY_WEIGHTED",
    #     "name": "Equally Weighted G2 Basket",
    #     "description": "Equally weighted portfolio of 2 main cryptocurrencies.",
    # },
    # {
    #     "ticker": "GOLD_CRYPTO_50_50",
    #     "name": "Gold Crypto 50-50 Basket",
    #     "description": "Gold & Crypto Portfolio 50/50",
    # },
    # {
    #     "ticker": "GOLD_CRYPTO_70_30",
    #     "name": "Gold Crypto 70-30 Basket",
    #     "description": "Gold & Crypto Portfolio 70/30",
    # },
    # {
    #     "ticker": "COINFOLIO_GOLD_CRYPTO",
    #     "name": "Gold Crypto Basket",
    #     "description": "Gold & Crypto Portfolio",
    # },
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
        cryptocurrency_quotes_collection, cryptocurrency, START_DATE, END_DATE)


# --------------------------------------------------------------------
# STRATEGIES WEIGHTS
# --------------------------------------------------------------------
# clean the database collection
strategies_weights_collection = database["strategies_weights"]
strategies_weights_collection.drop()

dates_list_for_period = get_dates_for_period(START_DATE, END_DATE)

for strategy in STRATEGIES:
    print("creating strategy weights for strategy: " + strategy["ticker"])
    for date in dates_list_for_period:
        create_strategy_weights(database,
                                strategy["ticker"], date)


# --------------------------------------------------------------------
# STRATEGIES BACKTESTS
# --------------------------------------------------------------------
# create backtest for the G4 strategy...

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


def run_backtest(strategy_info, backtest_data, start_portfolio):
    def append_next_porfolio(portfolios_series, backtest_data_item):
        weights = backtest_data_item["weights"]
        prices = backtest_data_item["prices"]
        date = backtest_data_item["date"]
        last_portfolio = portfolios_series[-1]
        next_portfolio = backtest.create_next_portfolio(
            last_portfolio, weights, prices, date, strategy_info)
        portfolios_series.append(next_portfolio)
        return portfolios_series

    portfolios_series = functools.reduce(append_next_porfolio,
                                         backtest_data, [start_portfolio])
    return portfolios_series


def load_backtest_into_database(database, strategy_ticker, start_date, end_date):

    strategy_info = strategiesDB.get_strategy_info(database, strategy_ticker)
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
        "commission": 0.001,
        "positions": [],
        "transactions": [],
        "date": first_backtest_date,
        "positions_market_value": 0,
        "total_value": 10000,
        "commissions_paid": 0,
        "total_commissions_paid": 0,
        "rebalanced_at": None,
    }

    # pass strategy metadata into here. e.g. rebalancing frequency
    portfolios_series = run_backtest(strategy_info, backtest_data, portfolio_0)

    for portfolio_item in portfolios_series:
        database["strategies_backtests"].insert_one(portfolio_item)


for strategy in STRATEGIES:
    print("creating and loading backtest for: " + strategy["ticker"])
    strategy_weights_info = strategiesDB.get_strategy_weights_info(
        database, strategy["ticker"])
    min_date = strategy_weights_info["min_date"]
    max_date = strategy_weights_info["max_date"]

    load_backtest_into_database(database,
                                strategy["ticker"], min_date, max_date)


client.close()
