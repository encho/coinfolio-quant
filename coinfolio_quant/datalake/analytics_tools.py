import pandas as pd
import numpy as np
from .market_data import get_field_dataframe


def series_correlation(series_1, series_2):
    """
        Computes the correlation between two timeseries, only utilizing the data available for both series.
        This is useful to compute correlations between cryptocurrencies, which have 7 days of prices/week and traditional
        assets, which may just have up to 5 active days/week.
    """
    series_1.name = "prices_1"
    series_2.name = "prices_2"
    df = pd.concat([series_1, series_2], axis=1)

    def nan_or_1(val):
        if (np.isnan(val)):
            return np.nan
        return 1

    def na_mask(row):
        price_1 = row["prices_1"]
        price_2 = row["prices_2"]
        if np.isnan(price_1) or np.isnan(price_2):
            return np.nan
        return 1.0

    df["na_mask"] = df.apply(na_mask, axis=1)
    df["prices_1_masked"] = df["na_mask"] * df["prices_1"]
    df["prices_2_masked"] = df["na_mask"] * df["prices_2"]

    df["prices_1_pct_change__AUXILIARY"] = df["prices_1_masked"].pct_change() * \
        df["prices_1"].apply(nan_or_1)
    df["prices_2_pct_change__AUXILIARY"] = df["prices_2_masked"].pct_change() * \
        df["prices_2"].apply(nan_or_1)
    correlation = df["prices_1_pct_change__AUXILIARY"].corr(
        df["prices_2_pct_change__AUXILIARY"])

    # correlation_old = series_1.pct_change().corr(series_2.pct_change())
    return correlation


def get_correlation_visualizer_data(database, first_asset, second_asset, start_date, end_date):

    first_asset_ticker = first_asset
    second_asset_ticker = second_asset

    first_asset_index = first_asset_ticker + "_INDEX"
    second_asset_index = second_asset_ticker + "_INDEX"

    first_asset_change = first_asset_ticker + "_SHIFT"
    second_asset_change = second_asset_ticker + "_SHIFT"

    def twr(percentage_return):
        if (np.isnan(percentage_return)):
            return 1
        return 1 + percentage_return

    df = get_field_dataframe(
        database, [first_asset_ticker, second_asset_ticker], start_date=start_date, end_date=end_date, field="close")

    df[first_asset_change] = df[first_asset_ticker].pct_change()
    df[second_asset_change] = df[second_asset_ticker].pct_change()

    df["twr_1"] = df[first_asset_change].apply(twr)
    df["twr_2"] = df[second_asset_change].apply(twr)

    df[first_asset_index] = 100 * df["twr_1"].cumprod()
    df[second_asset_index] = 100 * df["twr_2"].cumprod()

    correlation = series_correlation(
        df[first_asset_ticker], df[second_asset_ticker])

    data = [df[first_asset_index], df[second_asset_index]]
    headers = ["firstAsset", "secondAsset"]
    new_df = pd.concat(data, axis=1, keys=headers)

    return {
        "correlation": correlation,
        "series_df": new_df,
    }
