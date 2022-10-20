import datetime


# ---------------------------------------------------------------------
# TODO into etl utils
# ---------------------------------------------------------------------
def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%d")


def get_dates_for_period(start_date, end_date):
    dates = [start_date]
    current_date = start_date

    while current_date < end_date:
        next_day = current_date + datetime.timedelta(days=1)
        dates.append(next_day)
        current_date = next_day
    return dates
# ---------------------------------------------------------------------


def weights_series_collection(database):
    return database["strategies_weights"]


def metadata_collection(database):
    return database["strategies"]


def drop_metadata_collection(database):
    metadata_collection(database).drop()


def drop_weights_series_collection(database):
    weights_series_collection(database).drop()


def insert_metadata_list(database, strategies_metadata):
    collection = metadata_collection(database)
    for strategy in strategies_metadata:
        cleaned_strategy = strategy.copy()
        cleaned_strategy.pop("get_universe")
        cleaned_strategy.pop("get_weights")
        collection.insert_one(cleaned_strategy)


def create_strategy_weights(database, strategy_ticker, strategies_specs, date, upsert=False):
    # TODO make date_to_datetime function
    dt = datetime.datetime.combine(date, datetime.datetime.min.time())

    strategies_weights_collection = weights_series_collection(database)

    strategy_specs = list(filter(
        lambda it: it["ticker"] == strategy_ticker,
        strategies_specs
    ))
    if len(strategy_specs) != 1:
        raise Exception(
            "Either no STRATEGY_SPEC or too many for: " + strategy_ticker)
    strategy_spec = strategy_specs[0]

    currency_universe = strategy_spec["get_universe"](date)

    strategy_weights = strategy_spec["get_weights"](
        dt, currency_universe, database=database)

    if strategy_weights:

        strategy_weights_record = {
            "ticker": strategy_ticker,
            "date": dt,
            "weights": strategy_weights
        }

        if upsert == False:
            strategies_weights_collection.insert_one(strategy_weights_record)
        else:
            strategies_weights_collection.update_one({"ticker": strategy_ticker, "date": dt},
                                                     {"$set": strategy_weights_record}, upsert=True
                                                     )


def load_all_weights_series(DB, SPECS, START, END, upsert=False):
    dates_list_for_period = get_dates_for_period(START, END)
    for strategy in SPECS:
        print("creating strategy weights for strategy: " + strategy["ticker"])
        for date in dates_list_for_period:
            create_strategy_weights(DB,
                                    strategy["ticker"], SPECS, date, upsert=upsert)
