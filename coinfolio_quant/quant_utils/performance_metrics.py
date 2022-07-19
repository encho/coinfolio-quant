import numpy as np


def prices_to_returns(prices_series):
    return np.log(prices_series/prices_series.shift())


def sharpe_ratio(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    sr = returns_series.mean() / returns_series.std()
    ann_sr = sr * ann_factor**0.5
    return ann_sr


def total_return(prices_series):
    last_price = prices_series.iloc[-1]
    first_price = prices_series.iloc[0]
    return (last_price - first_price) / first_price


def annualized_return(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    mean_return = returns_series.mean()
    ann_mean_return = ann_factor * mean_return
    return ann_mean_return


def annualized_standard_deviation(prices_series, ann_factor=365):
    returns_series = prices_to_returns(prices_series)
    standard_deviation = returns_series.std()
    ann_standard_deviation = ann_factor**0.5 * standard_deviation
    return ann_standard_deviation


# gets a series with daily index values or prices
# returns a multiindex df with ["year", "month"] index
# and the columns: ["first", "last", "percentage_change"]
# e.g.:
#                    first          last  percentage_change
# year month
# 2020 1      10000.000000  11452.045665        0.145205
#      2      11472.667591  11006.300069       -0.040650
#      3      10987.215483  10168.793886       -0.074489
#      4      10254.259749  11913.120382        0.161773
#      5      12069.820135  12595.433054        0.043548
#      6      12973.200402  12673.616463       -0.023093
#      7      12639.119550  14586.855297        0.154104
#      8      14810.238209  14795.647240       -0.000985
#      9      14944.245681  13993.814904       -0.063598
#      10     14000.238943  15390.642081        0.099313
#      11     15370.918331  17196.317310        0.118757
#      12     17128.412268  20944.978042        0.222821
# 2021 1      21051.921588  21962.564366        0.043257
def monthly_returns_multiindex_df(prices_series):

    multi_index_df = prices_series.groupby(
        [prices_series.index.year, prices_series.index.month]).agg(["first", "last"])

    multi_index_df["percentage_change"] = (
        multi_index_df["last"] - multi_index_df["first"]) / multi_index_df["first"]

    multi_index_df.index.rename(["year", "month"], inplace=True)

    return multi_index_df


def series_performance_metrics(prices_series, ann_factor=365):

    monthly_returns_df = monthly_returns_multiindex_df(prices_series)
    max_index = monthly_returns_df["percentage_change"].idxmax()
    min_index = monthly_returns_df["percentage_change"].idxmin()
    max_return = monthly_returns_df.loc[max_index, "percentage_change"]
    min_return = monthly_returns_df.loc[min_index, "percentage_change"]

    performance_metrics = {
        "sharpe_ratio": sharpe_ratio(prices_series, ann_factor=ann_factor),
        "total_return": total_return(prices_series),
        "annualized_return": annualized_return(prices_series, ann_factor=ann_factor),
        "volatility": annualized_standard_deviation(prices_series, ann_factor=ann_factor),
        "best_month_return": max_return,
        "worst_month_return": min_return,
    }

    return performance_metrics
