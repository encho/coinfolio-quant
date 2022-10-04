import pandas as pd
import numpy as np
import coinfolio_quant.quant_utils.series_warnings as series_warnings

date_strings = ["2000-01-01", "2000-01-02", "2000-01-03"]
index = pd.DatetimeIndex(date_strings)
data = {'gold': [1, 2, np.nan], 'bitcoin': [3, 4, 5]}
df = pd.DataFrame(data=data, index=index)
# d = {'gold': [1, 2, 3], 'bitcoin': [3, 4, 5]}

print(df)


# # TODO test
# def get_index_with_last_number(series):
#     def is_number(x):
#         if type(x) == int or type(x) == float:
#             return True
#         else:
#             return False

#     for ix in map(lambda n: -1*(n+1), range(series.size)):
#         current_index = series.index[ix]
#         current_value = float(series.iloc[ix])

#         if is_number(current_value) and not np.isnan(current_value):
#             return current_index

#     raise Exception("no numeric value found in series")

# # TODO test


# def has_up_to_date_data(series):
#     last_number_index = get_index_with_last_number(series)
#     last_index = series.index[-1]
#     # print("last number index")
#     # print(last_number_index)
#     # print("last index")
#     # print(last_index)
#     is_ok = last_number_index == last_index
#     return is_ok

# # TODO test


# def get_series_warnings(dataframe):
#     warnings = {}
#     keys = dataframe.keys()
#     for k in keys:
#         print(k)
#         is_ok = has_up_to_date_data(dataframe[k])
#         if not is_ok:
#             warnings[k] = "Data not up to date"

#     if not bool(warnings):
#         return None

#     return warnings


# date_strings = ["2000-01-01", "2000-01-02", "2000-01-03"]
# index = pd.DatetimeIndex(date_strings)
# data = {'gold': [1, 2, np.nan], 'bitcoin': [3, 4, 5]}
# df = pd.DataFrame(data=data, index=index)

# gold_last_numeric_index = series_warnings.get_index_with_last_number(
#     df["gold"])
# assert(gold_last_numeric_index == index[1])

# bitcoin_last_numeric_index = series_warnings.get_index_with_last_number(
#     df["bitcoin"])

# assert(bitcoin_last_numeric_index == index[2])

# gold_warnings = series_warnings.has_up_to_date_data(df["gold"])


# print("**********")
# print("gold")
# print(gold_last_numeric_index)
# print("bitcoin")
# print(bitcoin_last_numeric_index)
# print("**********")

# gold_warnings = series_warnings.has_up_to_date_data(df["gold"])
# bitcoin_warnings = series_warnings.has_up_to_date_data(df["bitcoin"])

# print("**********")
# print("gold warnings")
# print(gold_warnings)

# print("bitcoin warnings")
# print(bitcoin_warnings)

print("wwwwwwwwwwwwwwww")
print("warnings")
www = series_warnings.get_series_warnings(df)
print(www)
