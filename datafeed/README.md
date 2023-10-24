# readme

[![](https://app.eraser.io/workspace/Dh05nL8Q247AgVP3jAmw/preview)]()

This is a docker-compose application that creates various images to create a realtime data analytics system.

This is a standalone application and should not be used in a production environment.

This system includes the following technologies
1. Redis
2. NodeJS
3. QuestDB
4. Python


### Redis
in-memory kv store. currently using pub/sub functionality by pushing/pulling from specific channel. Will implement timestreams as well. But typically data is pushed to an analytical/archival data store after being ingested. 


###  QuestDB
Timeseries optimized database built on top of Postgres

### Webserver
Currently using FastAPI as a backend to connect to QuestDB REST API
Endpoints are the specified queries built for the dashboard.

To create new queries you simply need to add your query to the queries.json file. You can then use them in the streamlit application by calling `hitEndpoint(key)`, where key is the key you specified in the json file. If you need to do extra processing or parameterize the query, you can create a new API endpoint in the FastAPI app. 

### Streamlit

Streamlit dashboard populates via the queries specified in the queries.json file. 

We achieve "pseudo realtime updates" by polling the database for the latest timestamp every N seconds and refresh data if newer timestamp arrives. 

## Producers

Uses nodejs to connect to websocket channel and produces messages to specified a redis channel. Separate script is running to capture and redirect data to QuestDB. Creating new methods of delivery will be instrumental. We want to be able to pull messages from our specific redis channel and push them out via webhook, rest, websocket, etc. 



### Datafeeds

We now are using Redis as a pub/sub broker to handle messages. We will have producers and consumers to and from the redis server populating a Postgres (QuestDB) database. 

We will have a FastAPI server running in order to connect to the QuestDB database. This webserver will be used via a Streamlit or Svelte web application to create and visualize data. 


Docker:
1. Redis - OSS
2. QuestDB - OSS
3. Backend Webserver
  - datafeeds/datafeed_webserver
4. Frontend hosting
  - Currently Streamlit, Soon to be Svelete
  - datafeeds/datafeed_streamlit is the current hosted version with src/pages holding page code
5. Producers
  - datafeeds/datafeed_producers

Use the docker compose file to start all services. Make sure to create the table in QuestDB or the streamlit application will not properly work. 

'CREATE TABLE binance_liquidations (ticker SYMBOL capacity 100 cache index capacity 4,
                   side SYMBOL capacity 5 cache index capacity 4,
                   exch SYMBOL capacity 5 cache index capacity 4,
                   amount FLOAT,
                   price FLOAT,
                  timestamp TIMESTAMP) 
                timestamp(timestamp);'