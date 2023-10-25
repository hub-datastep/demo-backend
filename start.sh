#!/bin/bash
nohup redis-server &
nohup rq worker --path src high default low &
python3 /app/src/app.py