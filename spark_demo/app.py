from flask import Flask, jsonify, request
import json
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)
sid = SentimentIntensityAnalyzer()

with open('queries.json') as f: queries = json.load(f)

def query_quest(query):
    import requests, json
    resp = requests.get('http://localhost:9000/exec',
                        {
                            'query': query,
                        })
    r = json.loads(resp.text)
    return r

@app.route('/predict', methods=['POST'])
def predict():
    result = sid.polarity_scores(request.get_json()['data'])
    return jsonify(result)

@app.route('/sum', methods=['POST'])
def sum():
    result = request.get_json()['data']
    print(result)
    return jsonify(result)

@app.route('/all', methods=['POST'])
def get_all():
    result = query_quest(queries['query'])
    return jsonify(result)

@app.route('/liqsHourly/<tf>', methods=['POST'])
def get_liqsHourly(tf):
    q = queries['liqsHourly'].format(tf[:-1])
    result = query_quest(q)
    return jsonify(result)

@app.route('/liqsMinutely/<tf>', methods=['POST'])
def get_liqsMinutely(tf):
    q = queries['liqsMinutely'].format(tf[:-1])
    result = query_quest(q)
    return jsonify(result)

@app.route('/amountLiqd', methods=['POST'])
def get_amtLiqd():
    result = query_quest(queries['amountLiqd'])
    return jsonify(result)

@app.route('/sampled15m', methods=['POST'])
def get_sampled15m():
    result = query_quest(queries['sampled15m'])
    return jsonify(result)

@app.route('/liqCountAmount', methods=['POST'])
def get_liqCountAmount():
    result = query_quest(queries['liqCountAmount'])
    return jsonify(result)

@app.route('/tickerLiqCountAmount/<ticker>', methods=['POST'])
def get_tickerLiqCountAmount(ticker):
    q = queries['tickerLiqCountAmount'].format(ticker)
    result = query_quest(q)
    return jsonify(result)

@app.route('/log', methods=['POST'])
def get_log():
    result = query_quest(queries['log'])
    return jsonify(result)

@app.route('/latestTs', methods=['POST'])
def get_latestTs():
    result = query_quest(queries['latestTs'])
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=1337)
