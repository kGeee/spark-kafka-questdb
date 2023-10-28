import json
from kafka import KafkaConsumer

bootstrap_servers="provider.bdl.computer:32397"
consumer = KafkaConsumer(
    'testinging',
     bootstrap_servers=bootstrap_servers,
     auto_offset_reset='earliest',
     enable_auto_commit=True,
     group_id='my-group',
     value_deserializer=lambda x: json.loads(x.decode('utf-8')))

for message in consumer:
    message = message.value
    print("consuming", message)