from pprint import pprint
import websocket as wb
import os,json,time,configparser
from kafka import KafkaProducer
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")
producer = KafkaProducer(bootstrap_servers=config['Kafka']['server'])
url = "wss://fstream.binance.com/stream?streams=!forceOrder@arr"
topic = 'binance_liquidations'

def on_open(ws):
    print("connection opened")

def on_close(ws):
    print("closed connection")


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    response = json.loads(message)
    # pprint(response)
    try:
        msg = {
            "ticker": response["data"]["o"]["s"],
            "side": "Short" if response["data"]["o"]["S"] == "BUY" else "Long",
            "exch": "BINANCE",
            "amount": round(
                float(response["data"]["o"]["q"])
                * float(response["data"]["o"]["p"]),
                4,
            ),
            "price": float(response["data"]["o"]["p"]),
            "timestamp": int(time.mktime(datetime.now().timetuple()) * 1000),
        }
        producer.send(topic, value=json.dumps(msg).encode("utf-8"))
    except Exception as e:
        pass

ws = wb.WebSocketApp(url, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()