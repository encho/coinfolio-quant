# import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies
# import coinfolio_quant.datalake.strategies as strategies

# import datalake.cryptocurrencies as cryptocurrencies
# import datalake.strategies as strategies

from prettyprinter import pprint
import pandas as pd


# TODO sort date ascending
def get_strategy_backtests_series(database, strategy_ticker, start_date=None, end_date=None):
    query_object = {"strategy_ticker": strategy_ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    result = database.strategies_backtests.find(query_object, {"_id": False})
    return list(result)


def get_strategy_backtests_series__total_value(database, strategy_ticker, start_date=None, end_date=None):
    query_object = {"strategy_ticker": strategy_ticker}

    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date

        query_object["date"] = date_query

    result = database.strategies_backtests.find(
        query_object, {"_id": False, "date": 1, "total_value": 1})
    return list(result)


# TODO: import strategies db module, s.t. etl also still works (and scripts!!!!)
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


def get_strategy_backtests_series__all__total_value(database):
    all_total_value_series = []
    for strategy in STRATEGIES:
        total_value_series = get_strategy_backtests_series__total_value(
            database, strategy["ticker"])
        all_total_value_series.append(total_value_series)

    zipped_series = zip(*all_total_value_series)

    result_series = []

    for zipped_series_items in list(zipped_series):
        result_series_item = {"date": zipped_series_items[0]["date"]}
        for (strategy_spec, series_item) in zip(STRATEGIES, zipped_series_items):
            result_series_item[strategy_spec["ticker"]
                               ] = series_item["total_value"]
            result_series.append(result_series_item)

    return pd.DataFrame(result_series)

    # portfolio namespace
    # ===========================================================

    # retrieves the data necessary to run a strategy backtest simulation
    # e.g. result
    # [
    #  {
    #     'date': datetime.datetime(2022, 6, 5),
    #     'weights': [
    #         {'ticker': 'BTC', 'weight': 0.5},
    #         {'ticker': 'ETH', 'weight': 0.5}
    #     ],
    #     'prices': {
    #         'ETH-USD': numpy.float64(1805.2049560546875),
    #         'BTC-USD': numpy.float64(29906.662109375)
    #     }
    # },
    # ..]

    # def get_backtest_data(database, strategy_ticker, currency, start_date, end_date):
    #     # TODO eventually into utils
    #     def make_row_dict(index, row):
    #         d = dict(row)
    #         d["date"] = index.to_pydatetime()
    #         return d

    #     necessary_tickers = strategies.get_strategy_tickers(
    #         database=database, ticker=strategy_ticker,
    #         start_date=start_date, end_date=end_date)

    #     cryptocurrency_exchange_rate_tickers = list(
    #         map(lambda cryptocurrency: cryptocurrency + "-" + currency, necessary_tickers))

    #     prices_df = cryptocurrencies.get_field_dataframe(
    #         database=database,
    #         tickers=cryptocurrency_exchange_rate_tickers,
    #         field="close",
    #         start_date=start_date,
    #         end_date=end_date
    #     )

    #     prices_list = [make_row_dict(index, row)
    #                    for index, row in prices_df.iterrows()]

    #     weights_list = strategies.get_strategy_weights_series(
    #         database=database, ticker=strategy_ticker,
    #         start_date=start_date, end_date=end_date)

    #     # safety check: check if its same dates
    #     prices_dates = list(map(lambda it: it["date"], prices_list))
    #     weights_dates = list(map(lambda it: it["date"], weights_list))
    #     assert(prices_dates == weights_dates)

    #     backtest_data_list = []
    #     for (weights_item, prices_item) in zip(weights_list, prices_list):
    #         del prices_item["date"]
    #         backtest_data_item = {
    #             "date": weights_item["date"],
    #             "weights": weights_item["weights"],
    #             "prices": prices_item,
    #         }
    #         backtest_data_list.append(backtest_data_item)

    #     return backtest_data_list
