# import yfinance as yf
# import progressbar
import datetime
import pandas as pd
import numpy as np
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies


def get_bitcoin_only_universe(date):
    return ["BTC"]


def get_g4_universe(date):
    return ["BTC", "ETH", "XRP", "ADA"]


def get_g2_universe(date):
    return ["BTC", "ETH"]


def get_gold_crypto_universe(date):
    return ["XAU", "BTC"]


def get_coinfolio_gold_crypto_universe(date):
    return ["XAU", "BTC", "ETH", "XRP", "ADA"]


def get_equally_weighted_asset_allocation(date, universe, database):
    currencies_amount = len(universe)
    return [{"ticker": ticker, "weight": 1/currencies_amount} for ticker in universe]


def get_60_40_asset_allocation(date, universe, database):
    return [{"ticker": universe[0], "weight": 0.6}, {"ticker": universe[1], "weight": 0.4}]


def get_70_30_asset_allocation(date, universe, database):
    return [{"ticker": universe[0], "weight": 0.7}, {"ticker": universe[1], "weight": 0.3}]


def get_coinfolio_gold_crypto_asset_allocation(date, universe, database):
    return [{"ticker": ticker, "weight": 0.6 if ticker == "XAU" else 0.4/4} for ticker in universe]


def get_single_long_only_asset_allocation(date, universe, database):
    # TODO throw error if universe longer than 1
    return [{"ticker": universe[0], "weight": 1}]


def get_inverted_volatility_asset_allocation(date, universe, database):

    # TODO into own module?
    def inverted_vola_weightings(list_of_volas):
        denominator = 0
        for vola in list_of_volas:
            denominator = denominator + 1/vola
        weights = [(1/vola) / denominator for vola in list_of_volas]
        return weights

    # TODO include in context
    base_currency = "USD"
    # TODO 360
    vola_days_period = 360

    start_date = date - datetime.timedelta(days=vola_days_period-1)

    price_tickers = list(
        map(lambda ticker: f'{ticker}-{base_currency}', universe))

    data = cryptocurrencies.get_field_dataframe(
        database, price_tickers, field="percentage_change", start_date=start_date, end_date=date)

    # QUICK-FIX we remove the weekdays again which were ffilled before in the etl pipeline
    # TODO: store w/o saturdays and sundays, s.t. this fix is not necessary
    data["weekday"] = pd.to_datetime(data.index).weekday
    data["is_weekday"] = data["weekday"] < 5
    data["quick_fix_factor"] = data["is_weekday"].replace(
        True, 1).replace(False, np.nan)
    data["XAU-USD"] = data["quick_fix_factor"] * data["XAU-USD"]

    data_start_date = data.index[0]
    is_data_valid = data_start_date == start_date

    if is_data_valid:
        std_dev = data.std()
        volas = [std_dev[f'{ticker}-{base_currency}'] for ticker in universe]
        weights = inverted_vola_weightings(volas)
        return [{"ticker": ticker, "weight": weight} for (ticker, weight) in zip(universe, weights)]

    return None


STRATEGIES_SPECS = [
    # {
    #     "ticker": "G4_EQUALLY_WEIGHTED",
    #     "get_universe": get_g4_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    # {
    #     "ticker": "G2_EQUALLY_WEIGHTED",
    #     "get_universe": get_g2_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    # {
    #     "ticker": "GOLD_CRYPTO_50_50",
    #     "get_universe": get_gold_crypto_universe,
    #     "get_weights": get_equally_weighted_asset_allocation
    # },
    {
        "ticker": "BITCOIN_ONLY",
        "get_universe": get_bitcoin_only_universe,
        "get_weights": get_single_long_only_asset_allocation,
    },
    {
        "ticker": "CFBG1",
        "get_universe": get_gold_crypto_universe,
        "get_weights": get_inverted_volatility_asset_allocation,
    },
    {
        "ticker": "CFGB2",
        "get_universe": get_gold_crypto_universe,
        "get_weights": get_inverted_volatility_asset_allocation,
    },
    {
        "ticker": "GOLD_CRYPTO_60_40",
        "get_universe": get_gold_crypto_universe,
        "get_weights": get_60_40_asset_allocation,
    },
    # {
    #     "ticker": "GOLD_CRYPTO_70_30",
    #     "get_universe": get_gold_crypto_universe,
    #     "get_weights": get_70_30_asset_allocation
    # },
    # {
    #     "ticker": "COINFOLIO_GOLD_CRYPTO",
    #     "get_universe": get_coinfolio_gold_crypto_universe,
    #     "get_weights": get_coinfolio_gold_crypto_asset_allocation
    # }
]


def create_strategy_weights(database, strategy_ticker, date):

    strategies_weights_collection = database["strategies_weights"]

    strategy_specs = list(filter(
        lambda it: it["ticker"] == strategy_ticker,
        STRATEGIES_SPECS
    ))
    if len(strategy_specs) != 1:
        raise Exception(
            "Either no STRATEGY_SPEC or too many for: " + strategy_ticker)
    strategy_spec = strategy_specs[0]

    currency_universe = strategy_spec["get_universe"](date)

    strategy_weights = strategy_spec["get_weights"](
        date, currency_universe, database=database)

    if strategy_weights:

        strategy_weights_record = {
            "ticker": strategy_ticker,
            "date": date,
            "weights": strategy_weights
        }

        strategies_weights_collection.insert_one(strategy_weights_record)
