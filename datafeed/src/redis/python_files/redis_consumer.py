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
    r = await redis.from_url("redis://localhost")
    async with r.pubsub() as pubsub:
        await pubsub.psubscribe("channel:*")

        future = asyncio.create_task(reader(pubsub))
        await future
        
asyncio.run(main())