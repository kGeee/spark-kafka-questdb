#!/bin/bash
python3 create_connect_sink.py
streamlit run dashapp.py & python3 webserver/app.py