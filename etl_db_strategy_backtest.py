import datetime
import pandas as pd
from prettyprinter import pprint
import functools

# import coinfolio_quant datalake accessors
import coinfolio_quant.datalake.strategies as strategiesDB
import coinfolio_quant.datalake.backtest as backtestDB
import coinfolio_quant.datalake.market_data as marketDataDB

# import coinfolio_quant backtest functionality
import coinfolio_quant.portfolio.backtest as backtest

# ---------------------------------------------------------------------
# TODO into etl utils
# ---------------------------------------------------------------------


def get_dates_for_period(start_date, end_date):
    dates = [start_date]
    current_date = start_date

    while current_date < end_date:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates


def get_datetimes_for_period(start_date, end_date):
    start_date = datetime.datetime.combine(
        start_date, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(
        end_date, datetime.datetime.min.time())

    dates = [start_date]
    current_date = start_date

    while current_date < end_date:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates

# ---------------------------------------------------------------------


def backtest_series_collection(database):
    return database["strategies_backtests"]


def drop_backtest_series_collection(database):
    backtest_series_collection(database).drop()


def get_backtest_data(database, strategy_ticker, currency, start_date, end_date):

    # ensure we are using datetime for mongodb operations
    # TODO make date_to_datetime function
    start_date = datetime.datetime.combine(
        start_date, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(
        end_date, datetime.datetime.min.time())

    # TODO eventually into utils
    def make_row_dict(index, row):
        d = dict(row)
        d["date"] = index.to_pydatetime()
        return d

    necessary_tickers = strategiesDB.get_strategy_tickers(
        database=database, ticker=strategy_ticker,
        start_date=start_date, end_date=end_date)

    # return necessary_tickers

    cryptocurrency_exchange_rate_tickers = list(
        map(lambda cryptocurrency: cryptocurrency + "-" + currency, necessary_tickers))

    weights_list = strategiesDB.get_strategy_weights_series(
        database=database, ticker=strategy_ticker,
        start_date=start_date, end_date=end_date)

    # return cryptocurrency_exchange_rate_tickers
    prices_df = marketDataDB.get_field_dataframe(
        database=database,
        tickers=cryptocurrency_exchange_rate_tickers,
        field="close",
        start_date=start_date,
        end_date=end_date
    )

    idx = pd.date_range(min(prices_df.index), max(prices_df.index))
    prices_df = prices_df.reindex(idx, method="ffill")
    prices_df.fillna(method="ffill", inplace=True)

    # here we ensure the prices have the same index as the weights (which should be daily 7 days a week)
    prices_df = prices_df.reindex(
        list(map(lambda it: it["date"], weights_list)))

    prices_list = [make_row_dict(index, row)
                   for index, row in prices_df.iterrows()]

    # sanity check: check if its same dates
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


def load_backtest_into_database_UPDATE(database, strategy_ticker, start_date, end_date):
    strategy_info = strategiesDB.get_strategy_info(database, strategy_ticker)
    update_dates = get_datetimes_for_period(start_date, end_date)

    for current_date in update_dates:
        print("updating portfolio for the date:")
        print(strategy_ticker)
        print(current_date)

        day_of_previous_backtest = current_date - datetime.timedelta(days=1)

        previous_backtest = backtestDB.get_backtest_for_date(
            database, "CFBG1", day_of_previous_backtest)

        necessary_tickers = strategiesDB.get_strategy_tickers(
            database=database, ticker=strategy_ticker,
            start_date=current_date, end_date=current_date)

        cryptocurrency_exchange_rate_tickers = list(
            map(lambda cryptocurrency: cryptocurrency + "-" + previous_backtest["currency"], necessary_tickers))

        prices = marketDataDB.get_field_dict_for_date(
            database, cryptocurrency_exchange_rate_tickers, current_date, "close")

        weights_result = strategiesDB.get_strategy_weights_for_date(
            database, strategy_ticker, current_date)
        weights = weights_result["weights"]

        current_portfolio_item = backtest.create_next_portfolio(
            previous_backtest, weights, prices, current_date, strategy_info)

        backtest_series_collection(database).update_one({"strategy_ticker": strategy_ticker, "date": current_date},
                                                        {"$set": current_portfolio_item}, upsert=True
                                                        )


def load_backtest_into_database_FIRST_RUN(database, strategy_ticker):

    strategy_weights_info = strategiesDB.get_strategy_weights_info(
        database, strategy_ticker)

    start_date = strategy_weights_info["min_date"]
    end_date = strategy_weights_info["max_date"]

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
        "strategy_weights": []
    }

    portfolios_series = run_backtest(strategy_info, backtest_data, portfolio_0)

    for portfolio_item in portfolios_series:
        backtest_series_collection(database).insert_one(portfolio_item)


def load_all_backtests_into_database_FIRST_RUN(database, strategies_specs):
    for strategy in strategies_specs:
        print("creating and loading backtest for: " + strategy["ticker"])
        load_backtest_into_database_FIRST_RUN(database,
                                              strategy["ticker"])


def load_all_backtests_into_database_UPDATE(database, strategies_specs, start_date, end_date):
    for strategy in strategies_specs:
        print("updating backtest for: " + strategy["ticker"])
        load_backtest_into_database_UPDATE(database,
                                           strategy["ticker"], start_date, end_date)
