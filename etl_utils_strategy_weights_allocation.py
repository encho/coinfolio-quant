import datetime
import pandas as pd
import numpy as np
import coinfolio_quant.datalake.cryptocurrencies as cryptocurrencies
import coinfolio_quant.datalake.market_data as marketDataDB


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


def make_inv_vola_aa(vola_days):
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
        # vola_days_period = 360
        vola_days_period = vola_days

        start_date = date - datetime.timedelta(days=vola_days_period-1)

        price_tickers = list(
            map(lambda ticker: f'{ticker}-{base_currency}', universe))

        # data = cryptocurrencies.get_field_dataframe(
        data = marketDataDB.get_field_dataframe(
            database, price_tickers, field="percentage_change", start_date=start_date, end_date=date)

        # QUICK-FIX we remove the weekdays again which were ffilled before in the etl pipeline
        # TODO: store w/o saturdays and sundays, s.t. this fix is not necessary
        # data["weekday"] = pd.to_datetime(data.index).weekday
        # data["is_weekday"] = data["weekday"] < 5
        # data["quick_fix_factor"] = data["is_weekday"].replace(
        #     True, 1).replace(False, np.nan)
        # data["XAU-USD"] = data["quick_fix_factor"] * data["XAU-USD"]

        # data_start_date = data.index[0]
        # is_data_valid = data_start_date == start_date

        is_data_valid = True

        if is_data_valid:
            std_dev = data.std()
            volas = [std_dev[f'{ticker}-{base_currency}']
                     for ticker in universe]
            weights = inverted_vola_weightings(volas)
            return [{"ticker": ticker, "weight": weight} for (ticker, weight) in zip(universe, weights)]

        return None

    return get_inverted_volatility_asset_allocation
