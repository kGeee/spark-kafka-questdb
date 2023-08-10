#!/bin/bash
docker exec -d python-playground python work/producers/binance_liq_producer.py
python3 src/webserver/app.py & streamlit run src/dashapp.py 