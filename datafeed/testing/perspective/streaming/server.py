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
import asyncio

from connectors.Quest import Quest
from functools import partial

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

    quest_url = "24.144.80.103:9000"
    quest = Quest(quest_url)

    def updater():
        data = quest.get_data()
        table.update(data)

    b = tornado.ioloop.PeriodicCallback(partial(updater,), 1000)

    psp_loop = tornado.ioloop.IOLoop()

    manager.set_loop_callback(psp_loop.add_callback)
    b.start()
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
    app.listen(8888)
    logging.critical("Listening on http://localhost:8888")
    loop = tornado.ioloop.IOLoop.current()
    loop.start()


