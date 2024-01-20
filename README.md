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
(venv) ➜  coinfolio-quant git:(main) COINFOLIO_BASE_URL=https://nerdy.finance FLASK_ENV=development MONGO_CONNECTION_STRING=mongodb://127.0.0.1:27017 python -m app
```

Note: COINFOLIO_BASE_URL is not used any more, I have for now just put a random url. This needs to be deprecated!

## ETL scripts

Load the crypto histories into the database:

```
MONGO_CONNECTION_STRING=mongodb://127.0.0.1:27017 python ./etl-reset.py
```

## IPython

Print current working directory from IPython shell:

```
!pwd
```
