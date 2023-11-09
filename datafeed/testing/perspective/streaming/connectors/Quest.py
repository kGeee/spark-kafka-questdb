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