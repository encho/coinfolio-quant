import os
from pymongo import MongoClient
import pandas as pd
import coinfolio_quant.datalake.cryptocurrencies as crypto

MONGO_CONNECTION_STRING = os.environ["MONGO_CONNECTION_STRING"]

client = MongoClient(MONGO_CONNECTION_STRING)
database = client["coinfolio_prod"]


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

data = [{"ticker": it["_id"], "min_date": it["min_date"],
         "max_date": it["max_date"]} for it in result]

print(data)
