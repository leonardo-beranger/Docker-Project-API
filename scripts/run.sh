#!/bin/sh

mkdir ~p /data/logs
mkdir ~p /data/json

export PRODUCTION=1
/home/doctor_dock/venv/bin/python /app/app.py --produtos --carts