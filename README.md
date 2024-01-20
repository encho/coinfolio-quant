# README

## Run Locally

Activate the virtual environment:

```
source venv/bin/activate
```

Run locally:

```
(venv) ➜  coinfolio-quant git:(main) COINFOLIO_BASE_URL=https://nerdy.finance FLASK_ENV=development MONGO_CONNECTION_STRING=mongodb://127.0.0.1:27017 python -m app
```

Note: COINFOLIO_BASE_URL is not used any more, I have for now just put a random url. This needs to be deprecated!

## ETL scripts

### Reset the local database

Load the crypto histories into the database:

```
MONGO_CONNECTION_STRING=mongodb://127.0.0.1:27017 python ./etl-reset.py
```

To reset the STAGE or PROD databases, run the above command with the respective MONGO_CONNECTION_STRING environment variable.

## Info: Manage Virtual Environment

Install virtualenv for python 3:

```
sudo pip3 install virtualenv
```

Create a virtual environment named `venv`:

```
virtualenv -p python3 venv
```

Activate the virtual environment:

```
source venv/bin/activate
```

Deactivate the virtual environment:

```
deactivate
```
