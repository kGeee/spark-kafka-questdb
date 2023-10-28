import websocket as wb
import json
from kafka import KafkaProducer
import time
from datetime import datetime

bootstrap_servers="provider.bdl.computer:32397"
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)


url = "wss://fstream.binance.com/stream?streams=!forceOrder@arr"
topic = 'testinging'

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
        print("producing", msg['ticker'])
        producer.send(topic, value=json.dumps(msg).encode("utf-8"))
        
    except Exception:
        pass

    

ws = wb.WebSocketApp(url, on_open=on_open, on_close=on_close, on_error=on_error,
                      on_message=on_message)
ws.run_forever()