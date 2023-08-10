from pprint import pprint
import os
import websocket as wb
from pprint import pprint
import json
from kafka import KafkaProducer
import time
from datetime import datetime

producer = KafkaProducer(bootstrap_servers="broker:29092")
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
            "amount": round(
                float(response["data"]["o"]["q"])
                * float(response["data"]["o"]["p"]),
                4,
            ),
            "price": float(response["data"]["o"]["p"]),
            "side": "Short" if response["data"]["o"]["S"] == "BUY" else "Long",
            "timestamp": int(time.mktime(datetime.now().timetuple()) * 1000),
            "exch": "BINANCE",
        }
        producer.send(topic, value=json.dumps(msg).encode("utf-8"))
    except Exception as e:
        pass

ws = wb.WebSocketApp(url, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()