import asyncio
import websockets
import json
from kafka import KafkaProducer
import time
from datetime import datetime

testing = False
if testing: producer = None
else: producer = KafkaProducer(bootstrap_servers="broker:29092")


async def nance_usdm_liq_ws():
    msg = {"method": "SUBSCRIBE", "params": ["!forceOrder@arr"], "id": 1}
    topic = "alt_liquidations"

    async with websockets.connect(
        "wss://fstream.binance.com/stream?streams=!forceOrder@arr"
    ) as ws:
        while True:
            await ws.send(json.dumps(msg))
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            response = json.loads(response)
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
                print(msg)
            except Exception as e:
                # print(f'Terminated', e)
                ws = await websockets.connect("wss://fstream.binance.com/stream?streams=!forceOrder@arr")
                

            await asyncio.sleep(2)


async def okx_liq_ws(type="SWAP"):
    msg = {
        "op": "subscribe",
        "args": [{"channel": "liquidation-orders", "instType": type}],
    }
    topic = "alt_liquidations"
    
    async with websockets.connect("wss://ws.okx.com:8443/ws/v5/public") as ws:
        while True:
            await ws.send(json.dumps(msg))
            response = await asyncio.wait_for(ws.recv(), timeout=30)
            response = json.loads(response)
            try:
                msg = {
                    "ticker": response["data"][0]["uly"][:-5],
                    "amount": round(
                        float(response["data"][0]["details"][0]["sz"])
                        * float(response["data"][0]["details"][0]["bkPx"]),
                        4,
                    ),
                    "price": float(response["data"][0]["details"][0]["bkPx"]),
                    "side": "Short"
                            if response["data"][0]["details"][0]["side"] == "buy"
                            else "Long",
                    "timestamp": int(time.mktime(datetime.now().timetuple()) * 1000),
                    "exch": "OKX",
                }
                if producer != None: producer.send(topic, value=json.dumps(msg).encode("utf-8"))
                else: print(msg)
            except websockets.ConnectionClosed as e:
                print(f'Terminated', e)
                ws = await websockets.connect("wss://ws.okx.com:8443/ws/v5/public")

            await asyncio.sleep(2)


async def multiple_tasks():
    input_coroutines = [nance_usdm_liq_ws(), okx_liq_ws(type="FUTURES")]
    await asyncio.gather(*input_coroutines, return_exceptions=True)

asyncio.get_event_loop().run_until_complete(nance_usdm_liq_ws())
