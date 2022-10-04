import pandas as pd
import numpy as np


def get_index_with_last_number(series):
    def is_number(x):
        if type(x) == int or type(x) == float:
            return True
        else:
            return False

    for ix in map(lambda n: -1*(n+1), range(series.size)):
        current_index = series.index[ix]
        current_value = float(series.iloc[ix])

        if is_number(current_value) and not np.isnan(current_value):
            return current_index

    raise Exception("no numeric value found in series")


date_strings = ["2000-01-01", "2000-01-02", "2000-01-03"]
index = pd.DatetimeIndex(date_strings)
data = {'gold': [1, 2, np.nan], 'bitcoin': [3, 4, 5]}
data_up_to_date = {'gold': [1, 2, 3], 'bitcoin': [3, 4, 5]}
df = pd.DataFrame(data=data, index=index)
df_up_to_date = pd.DataFrame(data=data_up_to_date, index=index)

gold_last_numeric_index = get_index_with_last_number(
    df["gold"])
assert(gold_last_numeric_index == index[1])

bitcoin_last_numeric_index = get_index_with_last_number(
    df["bitcoin"])

assert(bitcoin_last_numeric_index == index[2])


def has_up_to_date_data(series):
    last_number_index = get_index_with_last_number(series)
    last_index = series.index[-1]
    is_ok = last_number_index == last_index
    return is_ok


assert(has_up_to_date_data(df["gold"]) == False)
assert(has_up_to_date_data(df["bitcoin"]) == True)


def get_series_warnings(dataframe):
    warnings = {}
    keys = dataframe.keys()
    for k in keys:
        print(k)
        is_ok = has_up_to_date_data(dataframe[k])
        if not is_ok:
            warnings[k] = "Data not up to date"

    if not bool(warnings):
        return None

    return warnings


assert(get_series_warnings(df) == {"gold": "Data not up to date"})
assert(get_series_warnings(df_up_to_date) == None)
