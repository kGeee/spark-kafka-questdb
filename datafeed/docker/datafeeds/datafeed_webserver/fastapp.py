import uvicorn
import json
import httpx
import os
from perspective import PerspectiveManager, PerspectiveHandlerBase
import threading
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse


from perspective_src.perspectiveThread import perspective_thread

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
@app.route('/')
async def homepage(request):
    return FileResponse('static/index.html')
    
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

with open('queries.json') as f: queries = json.load(f)

async def query_quest(query):
    timeout=httpx.Timeout(30, read=30)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"http://{os.environ['QUEST_URL']}:9000/exec", params={'query': query})
    except httpx.ReadTimeout:
        resp = await query_quest(query)
    return json.loads(resp.text)

@app.get('/query/{key}')
async def get_keyedQuery(key):
    result = await query_quest(queries[key])
    return result

@app.get('/latestTs')
async def get_latestTs():
    result = await query_quest(queries['latestTs'])
    return result

@app.get('/tickerLiqCountAmount/{ticker}')
async def get_tickerLiqCountAmount(ticker):
    q = queries['tickerLiqCountAmount'].format(ticker)
    result = await query_quest(q)
    return result

@app.get('/liqsHourly/{tf}')
async def get_liqsHourly(tf):
    q = queries['liqsHourly'].format(tf[:-1])
    result = await query_quest(q)
    return result

@app.get('/liqsMinutely/{tf}')
async def get_liqsMinutely(tf):
    q = queries['liqsMinutely'].format(tf[:-1])
    result = await query_quest(q)
    return result

if __name__=='__main__':
    manager = PerspectiveManager()

    thread = threading.Thread(target=perspective_thread, args=(manager,))
    thread.daemon = True
    thread.start()

    uvicorn.run(app, host='0.0.0.0', 
                port=int(os.environ['WEBSERVER_PORT']),
                ssl_keyfile=os.environ['WEBSERVER_SSL_KEYFILE'],
                ssl_certfile=os.environ['WEBSERVER_SSL_CERTFILE'],)