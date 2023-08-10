import requests, time
while True:
  data = {
      "name": "liqs",
      "config": {
        "connector.class":"io.questdb.kafka.QuestDBSinkConnector",
        "tasks.max":"1",
        "topics": "binance_liquidations",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "key.converter.schemas.enable": "false",
        "value.converter.schemas.enable": "false",
        "host": "provider.bdl.computer:31103",
        "timestamp.field.name": "timestamp"
      }
    }
  try:
    print(requests.post('http://localhost:8083/connectors', json=data).text)
    break
  except:
    print("not ready")
    time.sleep(1)