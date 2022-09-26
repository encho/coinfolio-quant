import pandas as pd


import pandas as pd
from .cryptocurrencies import get_field_dataframe


def get_correlation_visualizer_data(database, first_asset, second_asset, start_date, end_date):

    first_asset_ticker = first_asset
    second_asset_ticker = second_asset

    first_asset_index = first_asset_ticker + "_INDEX"
    second_asset_index = second_asset_ticker + "_INDEX"

    first_asset_change = first_asset_ticker + "_SHIFT"
    second_asset_change = second_asset_ticker + "_SHIFT"

    df = get_field_dataframe(
        database, [first_asset_ticker, second_asset_ticker], start_date=start_date, end_date=end_date, field="close")

    df[first_asset_index] = 100 * df[first_asset_ticker] / \
        df[first_asset_ticker].iloc[0]

    df[second_asset_index] = 100 * df[second_asset_ticker] / \
        df[second_asset_ticker].iloc[0]

    df[first_asset_change] = df[first_asset_index].pct_change()
    df[second_asset_change] = df[second_asset_index].pct_change()

    correlation = df[first_asset_change].corr(df[second_asset_change])

    data = [df[first_asset_index], df[second_asset_index]]
    headers = ["firstAsset", "secondAsset"]
    new_df = pd.concat(data, axis=1, keys=headers)

    return {
        "correlation": correlation,
        "series_df": new_df,
    }
