import pandas as pd
import numpy as np
import coinfolio_quant.quant_utils.series_warnings as series_warnings

date_strings = ["2000-01-01", "2000-01-02", "2000-01-03"]
index = pd.DatetimeIndex(date_strings)
data = {'gold': [1, 2, np.nan], 'bitcoin': [3, 4, 5]}
df = pd.DataFrame(data=data, index=index)

print(df)

print("wwwwwwwwwwwwwwww")
print("warnings")
www = series_warnings.get_series_warnings(df)
print(www)
