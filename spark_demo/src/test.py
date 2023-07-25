import requests
data = {
  "name": "questdb-sink-bfx-btc",
  "config": {
    "connector.class":"io.questdb.kafka.QuestDBSinkConnector",
    "tasks.max":"1",
    "topics": "trades-BITFINEX-BTC-USD",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter.schema.registry.url": "https://psrc-j55zm.us-central1.gcp.confluent.cloud",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter.schemas.enable": "true",
    "insert.mode": "insert",
    "host": "questdb",
    "timestamp.field.name": "timestamp",
    "symbols":"symbol"
  }
}
requests.post('http://localhost:8083/connectors', json=data)
