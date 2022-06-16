import os
import coinfolio_quant.datalake.backtest as datalake_backtest
from pymongo import MongoClient
from prettyprinter import pprint
import datetime
import functools
import coinfolio_quant.portfolio.backtest as backtest

# **************************************************************
# THE SCRIPT
# **************************************************************
MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]

zero_date = datetime.datetime(2022, 6, 3)

backtest_data = datalake_backtest.get_backtest_data(
    database=database,
    strategy_ticker="G2_EQUALLY_WEIGHTED",
    currency="USD",
    start_date=datetime.datetime(2022, 6, 4),
    end_date=datetime.datetime(2022, 6, 9)
)

portfolio_0 = {
    "currency": "USD",
    "cash": 10000,
    "commission": 0.005,
    "positions": [],
    "transactions": [],
    "date": zero_date,
    "positions_market_value": 0,
    "total_value": 10000,
    "commissions_paid": 0,
    "total_commissions_paid": 0,
}

# etl function to create and store backtest in datalake


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


portfolios_series = run_backtest(backtest_data, portfolio_0)


print("&&&&&&&&&&")
print("&&&&&&&&&&")
pprint(portfolios_series)
print("&&&&&&&&&&")
print("&&&&&&&&&&")
