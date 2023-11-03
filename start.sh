#!/bin/sh
nohup redis-server &
nohup rq worker --path src default &
python3 /app/src/app.py
