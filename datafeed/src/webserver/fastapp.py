import uvicorn
from fastapi import FastAPI, BackgroundTasks
import json
import httpx

app = FastAPI()

with open('queries.json') as f: queries = json.load(f)

async def query_quest(query):
    timeout=httpx.Timeout(30, read=30)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"http://provider.pcgameservers.com:31182/exec", params={'query': query})
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
    uvicorn.run(app, host='0.0.0.0', port=8080)