import asyncio

import redis.asyncio as redis

STOPWORD = "STOP"


async def reader(channel: redis.client.PubSub):
    while True:
        message = await channel.get_message(ignore_subscribe_messages=True)
        if message is not None:
            print(f"(Reader) {message['channel'].decode()}: {message['data'].decode()}")
            if message["data"].decode() == STOPWORD:
                print("(Reader) STOP")
                break

async def main():
    r = await redis.Redis(host="http://provider.bdl.compute", port =30798, socket_keepalive=True)
    async with r.pubsub() as pubsub:
        await pubsub.psubscribe("liqs:binance")
        future = asyncio.create_task(reader(pubsub))
        await future
        
asyncio.run(main())