import datetime
from dateutil.relativedelta import relativedelta


def get_first_day_of_the_quarter(p_date: datetime.date):
    return datetime.datetime(p_date.year, 3 * ((p_date.month - 1) // 3) + 1, 1)


assert get_first_day_of_the_quarter(datetime.datetime(
    2020, 10, 5).date()) == datetime.datetime(2020, 10, 1)
assert get_first_day_of_the_quarter(datetime.datetime(
    2020, 9, 25).date()) == datetime.datetime(2020, 7, 1)
assert get_first_day_of_the_quarter(datetime.datetime(
    2020, 12, 11).date()) == datetime.datetime(2020, 10, 1)
assert get_first_day_of_the_quarter(datetime.datetime(
    2020, 1, 2).date()) == datetime.datetime(2020, 1, 1)


def get_first_day_of_the_year(p_date: datetime.date):
    return datetime.datetime(p_date.year, 1, 1)


assert get_first_day_of_the_year(datetime.datetime(
    2020, 10, 5).date()) == datetime.datetime(2020, 1, 1)
assert get_first_day_of_the_year(datetime.datetime(
    2022, 1, 3).date()) == datetime.datetime(2022, 1, 1)


def get_years_back_datetime(p_date: datetime.date, years_back: int):
    return datetime.datetime(p_date.year - years_back, p_date.month, p_date.day)


assert get_years_back_datetime(datetime.datetime(
    2020, 10, 5).date(), 1) == datetime.datetime(2019, 10, 5)

assert get_years_back_datetime(datetime.datetime(
    2020, 10, 5).date(), 2) == datetime.datetime(2018, 10, 5)

assert get_years_back_datetime(datetime.datetime(
    2020, 10, 5).date(), 0) == datetime.datetime(2020, 10, 5)


def get_shifted_date(end_date, time_period_string):
    if time_period_string == "1M":
        return end_date + relativedelta(months=-1)
    if time_period_string == "3M":
        return end_date + relativedelta(months=-3)
    if time_period_string == "6M":
        return end_date + relativedelta(months=-6)
    if time_period_string == "1Y":
        return end_date + relativedelta(years=-1)
    if time_period_string == "2Y":
        return end_date + relativedelta(years=-2)
    if time_period_string == "3Y":
        return end_date + relativedelta(years=-3)

    if time_period_string == "YTD":
        return get_first_day_of_the_year(end_date)
    if time_period_string == "QTD":
        return get_first_day_of_the_quarter(end_date)

    raise Exception("get_time_period: Unknown time_period_string")


test_today = datetime.datetime(2022, 9, 16)
assert get_shifted_date(test_today, "1M") == datetime.datetime(2022, 8, 16)
assert get_shifted_date(test_today, "3M") == datetime.datetime(2022, 6, 16)
assert get_shifted_date(test_today, "6M") == datetime.datetime(2022, 3, 16)
assert get_shifted_date(test_today, "1Y") == datetime.datetime(2021, 9, 16)
assert get_shifted_date(test_today, "2Y") == datetime.datetime(2020, 9, 16)
assert get_shifted_date(test_today, "3Y") == datetime.datetime(2019, 9, 16)
assert get_shifted_date(test_today, "YTD") == datetime.datetime(2022, 1, 1)
assert get_shifted_date(test_today, "QTD") == datetime.datetime(2022, 7, 1)
