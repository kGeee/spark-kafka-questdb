import json
import logging
import time
import asyncio
import multiprocessing
import threading
import tornado.ioloop

import json
import redis.asyncio as redis
import requests
import httpx


from functools import partial

from zlib import crc32

# A set of datasources designed to work with Tornado - instead of using
# multiprocessing, they submit all work to the Tornado IOLoop to be scheduled.


class BaseDataSource(object):
    def __init__(
        self, table, ioloop, data_cleaner=None
    ):
        """A base class for a datasource that feeds data into Perspective
        
        Subclasses must implement `get_data`, which retrieves data and
        updates the Perspective table.
        
        Args:
            table (perspective.Table) a Perspective table instance that will
                be updated with new data.
            
            ioloop (tornado.ioloop.IOLoop) a reference to a Tornado IOLoop.
                
        Keyword Args:
            data_cleaner (func) A function that receives data input and
                returns cleaned data before the Perspective table is updated.
        """
        self.table = table  # An already-created Perspective table
        self.ioloop = ioloop
        self._data_cleaner = data_cleaner

    def start(self):
        """Start both the data getter subprocess."""
        self.ioloop.add_callback(self.get_data)
        logging.info("[DataSource] Started")

    def get_data(self):
        """A method that gets data and updates the Perspective Table - must be
        implemented by the child class."""
        raise NotImplementedError("Not implemented!")


def bytes_to_float(b):
    return float(crc32(b) & 0xFFFFFFFF) / 2 ** 32


def str_to_float(s, encoding="utf-8"):
    return bytes_to_float(s.encode(encoding))


class QuestDataSource(BaseDataSource):
    def __init__(self, table, ioloop, quest_url, interval=5000, **kwargs):
        data_cleaner = None#kwargs.pop('data_cleaner')
        super(QuestDataSource, self).__init__(table,ioloop, data_cleaner=data_cleaner)
        self.quest_url = quest_url
        self.latestTs = "2023-08-10T00:41:54.000000Z"
        self._interval = interval
    
    def start(self):
        """Start both the data getter subprocess."""
        # self.ioloop.call_later(delay=0, callback=self.get_data)
        print("[DataSource] Started")
        callback = tornado.ioloop.PeriodicCallback(callback=self.get_data, callback_time=self._interval)
        callback.start()

    def get_latest_ts(self):
        q = "select max(timestamp) from 'binance_liquidations'"
        data = self.query_quest(q)
        return data[0][0]
        
    def query_quest(self, query):
        resp = requests.get(f"http://{self.quest_url}/exec", params={'query': query})
        return json.loads(resp.text)['dataset']
    
    def get_data(self):
        query = f"select * from binance_liquidations where timestamp > '{self.latestTs}'"
        
        data = self.query_quest(query)
        table_data = [{'ticker': row[0], 'side': row[1], 'exch': row[2], 'amount': row[3], 'price': row[4], 'ts': row[5]} for row in data]
        print(table_data)
        print(self.latestTs)
        self.table.update(table_data)
        self.latestTs = self.get_latest_ts()


class redisDataSource(BaseDataSource):
    def __init__(self, table, ioloop, redis_host, redis_port, **kwargs):
        self.table = table
        data_cleaner = None
        super(redisDataSource, self).__init__(table,ioloop, data_cleaner=data_cleaner)
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._redis_topic = kwargs.pop('topic')
    
    def start(self):
        """Start both the data getter subprocess."""
        self.ioloop.run_sync(self.main)
        logging.info("[DataSource] Started")

    def get_data(self, data):
        pass


    async def reader(self, channel: redis.client.PubSub):
        print(self.table)
        while True:
            message = await channel.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print(f"(Reader) {message['channel'].decode()}: {message['data'].decode()}")
                self.table.update(json.loads(message['data'].decode()))

    async def main(self):
        r = await redis.Redis(host=self._redis_host, port=self._redis_port, socket_keepalive=True)
        print("connected")
        async with r.pubsub() as pubsub:
            await pubsub.psubscribe(self._redis_topic)
            future = asyncio.create_task(self.reader(pubsub))
            await future