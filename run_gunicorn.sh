#!/usr/bin/env bash

source .env

gunicorn -c src/config/gunicorn.py src.app:app
