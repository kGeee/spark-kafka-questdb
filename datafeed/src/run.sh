#!/bin/bash
python3 create_connect_sink.py
docker exec -d python-playground python work/producers/binance_liq_producer.py
streamlit run dashapp.py & python3 webserver/app.py