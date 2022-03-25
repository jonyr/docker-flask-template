#!/usr/bin/env bash

source .env

gunicorn -c config/gunicorn.py wsgi:app
