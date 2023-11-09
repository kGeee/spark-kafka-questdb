from perspective import Table
from datetime import date, datetime
import os
import tornado.ioloop
from functools import partial
import requests, json

class Quest:
    def __init__(self, quest_url):
        self.quest_url = quest_url
        self.latest = "2023-08-10T00:41:54.000000Z"

    def get_latest_ts(self):
            q = "select max(timestamp) from 'binance_liquidations'"
            data = self.query_quest(q)
            return data[0][0]
            
    def query_quest(self, query):
        resp = requests.get(f"http://{self.quest_url}/exec", params={'query': query})
        return json.loads(resp.text)['dataset']

    def get_data(self):
        query = f"select * from binance_liquidations where timestamp > '{self.latest}'"
        data = self.query_quest(query)
        self.latest = self.get_latest_ts()
        table_data = [{'ticker': row[0], 'side': row[1], 'exch': row[2], 'amount': row[3], 'price': row[4], 'ts': row[5]} for row in data]
        return table_data
    
def perspective_thread(manager):
    """Perspective application thread starts its own tornado IOLoop, and
    adds the table with the name "data_source_one", which will be used
    in the front-end."""
    table = Table(
        {
            "ticker": str,
            "side": str,
            "exch": str,
            "amount": float,
            "price": float,
            "ts": datetime,
            
        },
        limit=2500,
    )

    manager.host_table("data_source_one", table)

    quest_url = os.environ['QUEST_URL'] + ":9000"
    quest = Quest(quest_url)

    def updater():
        data = quest.get_data()
        table.update(data)

    b = tornado.ioloop.PeriodicCallback(partial(updater,), 1000)

    psp_loop = tornado.ioloop.IOLoop()

    manager.set_loop_callback(psp_loop.add_callback)
    b.start()
    psp_loop.start()