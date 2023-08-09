import requests
data = {
    "name": "binance-usdm-liq",
    "config": {
      "connector.class":"io.questdb.kafka.QuestDBSinkConnector",
      "tasks.max":"1",
      "topics": "alt_liquidations",
      "key.converter": "org.apache.kafka.connect.storage.StringConverter",
      "value.converter": "org.apache.kafka.connect.json.JsonConverter",
      "key.converter.schemas.enable": "false",
      "value.converter.schemas.enable": "false",
      "host": "questdb",
      "timestamp.field.name": "timestamp"
    }
  }
print(requests.post('http://localhost:8083/connectors', json=data).text)
