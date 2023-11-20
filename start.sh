#!/bin/sh
nohup redis-server &
nohup rq worker --path src nomenclature document &
python3 /app/src/app.py
