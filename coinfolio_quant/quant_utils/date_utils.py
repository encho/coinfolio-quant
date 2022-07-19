import datetime


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
