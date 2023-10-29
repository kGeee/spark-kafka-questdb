#  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
#  ┃ ██████ ██████ ██████       █      █      █      █      █ █▄  ▀███ █       ┃
#  ┃ ▄▄▄▄▄█ █▄▄▄▄▄ ▄▄▄▄▄█  ▀▀▀▀▀█▀▀▀▀▀ █ ▀▀▀▀▀█ ████████▌▐███ ███▄  ▀█ █ ▀▀▀▀▀ ┃
#  ┃ █▀▀▀▀▀ █▀▀▀▀▀ █▀██▀▀ ▄▄▄▄▄ █ ▄▄▄▄▄█ ▄▄▄▄▄█ ████████▌▐███ █████▄   █ ▄▄▄▄▄ ┃
#  ┃ █      ██████ █  ▀█▄       █ ██████      █      ███▌▐███ ███████▄ █       ┃
#  ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
#  ┃ Copyright (c) 2017, the Perspective Authors.                              ┃
#  ┃ ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ ┃
#  ┃ This file is part of the Perspective library, distributed under the terms ┃
#  ┃ of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). ┃
#  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

import random
import logging
import threading
import tornado.websocket
import tornado.web
import tornado.ioloop
from datetime import date, datetime
from perspective import Table, PerspectiveManager, PerspectiveTornadoHandler
import threading
import concurrent.futures

from datasources.tornado_datasources import redisDataSource, QuestDataSource, BaseDataSource
import requests, json
from functools import partial

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

IS_MULTI_THREADED = False


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

    # Track the table with the name "data_source_one", which will be used in
    # the front-end to access the Table.
    manager.host_table("data_source_one", table)
    # table.update([{'ticker': 'PEOPLEUSDT', 'side': 'Short', 'exch': 'BINANCE', 'amount': 5198.54748, 'price': 0.01302, 'ts': '2023-10-27T09:50:32.492877Z'}])

    quest_url = "localhost:60755"

    quest = Quest(quest_url)
    # get seed data

    

    def updater():
        data = quest.get_data()
        table.update(data)

    # quest = QuestDataSource(table, tornado.ioloop.IOLoop(), quest_url="localhost:60755")
    b = tornado.ioloop.PeriodicCallback(partial(updater,), 1000)
    # base = BaseDataSource(table, tornado.ioloop.IOLoop())

    psp_loop = tornado.ioloop.IOLoop()
    if IS_MULTI_THREADED:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            manager.set_loop_callback(psp_loop.run_in_executor, executor)
            # base.start()
            b.start()
            psp_loop.start()
    else:
        manager.set_loop_callback(psp_loop.add_callback)
        b.start()
        # base.start()
        psp_loop.start()



def make_app():
    manager = PerspectiveManager()

    thread = threading.Thread(target=perspective_thread, args=(manager,))
    thread.daemon = True
    thread.start()

    return tornado.web.Application(
        [
            # create a websocket endpoint that the client Javascript can access
            (
                r"/websocket",
                PerspectiveTornadoHandler,
                {"manager": manager, "check_origin": True},
            ),
            (
                r"/node_modules/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "../../node_modules/"},
            ),
            (
                r"/(.*)",
                tornado.web.StaticFileHandler,
                {"path": "./", "default_filename": "index.html"},
            ),
        ]
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    logging.critical("Listening on http://localhost:8080")
    loop = tornado.ioloop.IOLoop.current()
    loop.start()


