import os
import websocket as wb
from pprint import pprint
import json
import time
from datetime import datetime
import requests

url = "wss://fstream.binance.com/stream?streams=!forceOrder@arr"
table = 'alt_liquidations'

def on_open(ws):
    print("connection opened")

def on_close(ws):
    print("closed connection")

def on_error(ws, error):
    print(error)

def insert(host, port, table, values):
        query = f"insert into {table} values ('{values['ticker']}', '{values['side']}', '{values['exch']}', {values['amount']}, {values['price']}, systimestamp())"
        r=requests.get(f"http://{host}:{port}/exec?query={query}")

def on_message(ws, message):
    response = json.loads(message)
    try:
        msg = { "ticker": response["data"]["o"]["s"],
                "side": "Short" if response["data"]["o"]["S"] == "BUY" else "Long",
                "exch": "BINANCE",
                "amount": round(
                    float(response["data"]["o"]["q"])
                    * float(response["data"]["o"]["p"]),
                    4,
                ),
                "price": float(response["data"]["o"]["p"])
            }
        insert("provider.bdl.computer", 31103, "binance_liquidations", msg)

    except Exception as e:
        pass

ws = wb.WebSocketApp(url, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()