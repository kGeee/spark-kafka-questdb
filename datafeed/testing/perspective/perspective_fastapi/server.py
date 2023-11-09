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
import concurrent.futures

from connectors.Quest import Quest
from functools import partial

import uvicorn
from fastapi import FastAPI, BackgroundTasks
from starlette.responses import FileResponse
from starlette.endpoints import WebSocketEndpoint, HTTPEndpoint
from perspective import Table, PerspectiveManager, PerspectiveHandlerBase
from starlette.routing import Route, WebSocketRoute
from starlette.responses import HTMLResponse
from starlette.applications import Starlette
import os

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

app = Starlette()

@app.route('/')
async def homepage(request):
    return FileResponse('index.html')
    

@app.websocket_route('/websocket')
async def websocket_endpoint(websocket):
    class PerspectiveHandler(PerspectiveHandlerBase):
        async def write_message(self, message: str, binary: bool = False):
            await websocket.send_bytes(message)
        
        def on_message(self, *args, **kwargs):
            return PerspectiveHandlerBase.on_message(self, *args, **kwargs)

    await websocket.accept()
    ph = PerspectiveHandler(**{'manager':manager, 'check_origin':True})
    # Process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await ph.on_message(message=mesg)
    await websocket.close()

if __name__ == "__main__":

    manager = PerspectiveManager()

    thread = threading.Thread(target=perspective_thread, args=(manager,))
    thread.daemon = True
    thread.start()

    uvicorn.run(app, host='0.0.0.0', port=8888)


    

