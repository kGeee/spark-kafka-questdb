import asyncio
import websockets
import redis.asyncio as redis
import json, time
from datetime import datetime
STOPWORD = "STOP"
async def writer(channel: redis.client.PubSub, chan, message):
    await channel.publish(f"channel:{chan}", message)

async def write(channel, msg):
    
    async with r.pubsub() as pubsub:
        await writer(r, channel, msg)

async def send_stop():
    r = await redis.from_url("redis://localhost")
    async with r.pubsub() as pubsub:
        await writer(r, 1, STOPWORD)

async def wsrun(uri="wss://fstream.binance.com/stream?streams=!forceOrder@arr"):
    r = await redis.from_url("redis://localhost")
    async with r.pubsub() as pubsub:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                response = json.loads(message)
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
                    print("producing", json.dumps(msg).encode("utf-8"))
                    await r.publish(f"channel:test", json.dumps(msg).encode("utf-8"))
                except Exception as e:
                    pass

asyncio.get_event_loop().run_until_complete(wsrun())

# loop = asyncio.get_event_loop()
# group1 = asyncio.gather(*[write(1, f"testing {i}") for i in range(1, 5)])
# group2 = asyncio.gather(*[write(2, f"testing {i}") for i in range(1, 5)])
# groups = asyncio.gather(group1, group2)
# results = loop.run_until_complete(groups)
# asyncio.run(send_stop())
# loop.close()
# print(results)
