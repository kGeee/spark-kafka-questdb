from flask import Flask, jsonify
import requests, json

app = Flask(__name__)

with open('webserver/queries.json') as f: queries = json.load(f)

def query_quest(query):
    resp = requests.get('http://localhost:9000/exec',
                        {'query': query})
    r = json.loads(resp.text)
    return r

@app.route('/query/<key>', methods=['GET','POST'])
def get_keyedQuery(key):
    result = query_quest(queries[key])
    return jsonify(result)

@app.route('/latestTs', methods=['GET','POST'])
def get_latestTs():
    result = query_quest(queries['latestTs'])
    return jsonify(result)

@app.route('/tickerLiqCountAmount/<ticker>', methods=['GET','POST'])
def get_tickerLiqCountAmount(ticker):
    q = queries['tickerLiqCountAmount'].format(ticker)
    result = query_quest(q)
    return jsonify(result)

@app.route('/liqsHourly/<tf>', methods=['GET','POST'])
def get_liqsHourly(tf):
    q = queries['liqsHourly'].format(tf[:-1])
    result = query_quest(q)
    return jsonify(result)

@app.route('/liqsMinutely/<tf>', methods=['GET','POST'])
def get_liqsMinutely(tf):
    q = queries['liqsMinutely'].format(tf[:-1])
    result = query_quest(q)
    return jsonify(result)
if __name__ == '__main__':
    app.run(port=1337)
