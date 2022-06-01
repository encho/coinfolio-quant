import pandas as pd
from flask import Flask
from flask_cors import CORS


# import json

app = Flask(__name__)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

CORS(app)


@app.route('/')
def hello_world():
    df = pd.DataFrame(
        [["a", "b"], ["c", "d"]],
        index=["row 1", "row 2"],
        columns=["col 1", "col 2"],
    )

    result = df.to_json(orient="table")
    return result


@app.route('/series')
def crypto_series():
    my_series = pd.Series([22, 35, 58, 89, 100, 50], name="value", index=pd.to_datetime(
        ["2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06"]))

    result = my_series.to_json(orient="table")
    return result


if __name__ == '__main__':
    app.run()
