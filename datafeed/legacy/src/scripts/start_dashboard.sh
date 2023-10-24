#!/bin/bash
#docker exec -d python-playground python work/producers/quest_db_producer.py
python3 src/webserver/fastapp.py & streamlit run src/dashapp.py 
