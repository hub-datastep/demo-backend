#!/bin/bash
nohup redis-server &
nohup rq worker --path src nomenclature &
python3 /app/src/app.py
