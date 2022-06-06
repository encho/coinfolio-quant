# README

This is the [Flask](http://flask.pocoo.org/) [quick start](http://flask.pocoo.org/docs/1.0/quickstart/#a-minimal-application) example for [Render](https://render.com).

The app in this repo is deployed at [https://flask.onrender.com](https://flask.onrender.com).

## Deployment

Follow the guide at https://render.com/docs/deploy-flask.

## Manage Virtual Environment

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

## Quant API Server

Run locally:

```
FLASK_ENV=development MONGO_CONNECTION_STRING=<mongo-conn-string> python -m app
```

## ETL scripts

Load the crypto histories into the database:

```
MONGO_CONNECTION_STRING=<mongo-conn-string> python ./etl/load_crypto_histories.py
```
