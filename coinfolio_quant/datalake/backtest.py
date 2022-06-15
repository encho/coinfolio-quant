import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies
import coinfolio_quant.datalake.strategies as strategies

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


def get_backtest_data(database, strategy_ticker, currency, start_date, end_date):
    # TODO eventually into utils
    def make_row_dict(index, row):
        d = dict(row)
        d["date"] = index.to_pydatetime()
        return d

    necessary_tickers = strategies.get_strategy_tickers(
        database=database, ticker=strategy_ticker,
        start_date=start_date, end_date=end_date)

    cryptocurrency_exchange_rate_tickers = list(
        map(lambda cryptocurrency: cryptocurrency + "-" + currency, necessary_tickers))

    prices_df = cryptocurrencies.get_field_dataframe(
        database=database,
        tickers=cryptocurrency_exchange_rate_tickers,
        field="close",
        start_date=start_date,
        end_date=end_date
    )

    prices_list = [make_row_dict(index, row)
                   for index, row in prices_df.iterrows()]

    weights_list = strategies.get_strategy_weights_series(
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
