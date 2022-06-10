import pandas as pd


def get_overview(database):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    print(cryptocurrency_quotes_collection)

    result = database.cryptocurrency_quotes.aggregate(
        [
            {
                "$group":
                {
                    "_id": "$ticker",
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"},
                }
            }
        ]
    )

    overview_table = [{"ticker": it["_id"], "min_date": it["min_date"],
                       "max_date": it["max_date"]} for it in result]

    return overview_table


def get_cryptocurrency_dataframe(database, ticker="hello"):
    cryptocurrency_quotes_collection = database["cryptocurrency_quotes"]
    cursor = cryptocurrency_quotes_collection.find(
        {"ticker": ticker}, {"_id": False})
    results_list = list(cursor)
    df = pd.DataFrame(results_list)
    return df
