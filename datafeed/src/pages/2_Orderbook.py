
# https://discuss.streamlit.io/t/can-i-animate-a-scatter-plot/2242/4

import time
import json
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import requests

class OrderBook:
    def __init__(self):
        self.agg_ob = {'asks': {}, 'bids': {}}
        self.trades = pd.DataFrame()

    def getCoinbase(self):
        print("getting coinbase data")
        def getBook():
            print("getting coinbase book")
            coin = {}
            headers = {
                    'Content-Type': 'application/json'
                    }
            r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/book?level=0", headers=headers)
            req_json = r.json()
            bids, asks = req_json['bids'], req_json['asks']

            coin['asks'] = {float(ask[0]):float(ask[1]) for ask in asks}
            coin['bids'] = {float(bid[0]):float(bid[1]) for bid in bids}

            self.add_to_agg_ob(coin)

        def getTrades():
            print("getting coinbase trades")
            headers = {
                    'Content-Type': 'application/json'
                    }
            r = requests.get("https://api.exchange.coinbase.com/products/BTC-USD/trades?limit=100", headers=headers)

            req_json = r.json()
            # self.trades = pd.DataFrame(req_json, columns=['trade_id','side', 'size', 'price', 'time'])
            self.trades = pd.concat([self.trades, pd.DataFrame(req_json, columns=['trade_id','side', 'size', 'price', 'time'])], ignore_index=True)
        getBook()
        getTrades()



    def getKraken(self):
        print("getting kraken data")
        def getBook():
            print("getting kraken book")
            kraken = {}
            headers = {
                    'Content-Type': 'application/json'
                    }
            r = requests.get("https://api.kraken.com/0/public/Depth?pair=XBTUSD", headers=headers)
            req_json = r.json()['result']['XXBTZUSD']
            bids, asks = req_json['bids'], req_json['asks']

            kraken['asks'] = {float(ask[0]):float(ask[1]) for ask in asks}
            kraken['bids'] = {float(bid[0]):float(bid[1]) for bid in bids}

            self.add_to_agg_ob(kraken)

        def getTrades():
            print("getting kraken trades")

            headers = {
                    'Content-Type': 'application/json'
                    }
            r = requests.get("https://api.kraken.com/0/public/Trades?pair=XBTUSD", headers=headers)
            req_json = r.json()['result']['XXBTZUSD']
            df = pd.DataFrame(req_json, columns=['price','size', 'time', 'side', 'market', 'trade_id'])
            
            self.trades = pd.concat([self.trades, df[['trade_id','side', 'size', 'price', 'time']]], ignore_index=True)
            print(self.trades)

        getBook()
        # getTrades()

    def getGemini(self):
        print("getting gemini book")
        gemini = {}
        headers = {
                'Content-Type': 'application/json'
                }
        r = requests.get("https://api.gemini.com/v1/book/BTCUSD", headers=headers)
        req_json = r.json()
        bids, asks = req_json['bids'], req_json['asks']

        gemini['asks'] = {float(ask['price']):float(ask['amount']) for ask in asks}
        gemini['bids'] = {float(bid['price']):float(bid['amount']) for bid in bids}

        return self.add_to_agg_ob(gemini)
        
    def add_to_agg_ob(self, exch):
        """
        Add the values from the 'asks' and 'bids' dictionaries in the 'exch' parameter to the 'agg_ob' dictionary.
        """
        for k,v in exch['asks'].items():
            try: self.agg_ob['asks'][k] += v
            except KeyError: self.agg_ob['asks'][k] = v

        for k,v in exch['bids'].items():
            try: self.agg_ob['bids'][k] += v
            except KeyError: self.agg_ob['bids'][k] = v

    def get_price_desired_amt(self, remaining_amt, side):
        """
        Get the cost of the desired amount of BTC at the desired price.
        """
        count = 0
        cost = 0
        for price,amt in self.agg_ob[side].items():
            if remaining_amt - amt >= 0:
                cost += price*amt
                count += amt
                remaining_amt -= amt
            else: 
                # take remaining at this price
                cost += price*remaining_amt
                count += remaining_amt
                remaining_amt = 0
                break
            
        return cost, remaining_amt


def transform_data(agg_ob):
    bids_price, bids_size, asks_price, asks_size = [], [], [], []
    for k,v in agg_ob.items():
        for price, depth in v.items():
            if k == 'asks':
                asks_price.append(price)
                asks_size.append(depth)
            else:
                bids_price.append(price)
                bids_size.append(depth)
    return bids_price, bids_size, asks_price, asks_size
    
if __name__ == "__main__":
    st.set_page_config(page_title="Orderbook", layout="wide")
    st_canvas = st.empty()
    st_vp = st.empty()
    st_trade_log = st.empty()

    hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        .css-zq5wmm {visibility: hidden;}
        </style>
        """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


    options = st.multiselect(
        'Orderbooks to aggregate?',
        ['Coinbase', 'Gemini', 'Kraken'],
        ['Coinbase', 'Gemini', 'Kraken'])

    while True:
        ob = OrderBook()
        if 'Coinbase' in options: ob.getCoinbase()
        if 'Gemini' in options: ob.getGemini()
        if 'Kraken' in options: ob.getKraken()
        
        bids_price, bids_size, asks_price, asks_size = transform_data(ob.agg_ob)
        
        bids = pd.DataFrame({'prices': bids_price, 'depths': bids_size, 'side':'bid'})
        asks = pd.DataFrame({'prices': asks_price, 'depths': asks_size, 'side':'ask'})
        orderbook = pd.concat([bids, asks])

        # https://stackoverflow.com/questions/62579826/altair-bar-chart-assign-specific-colors-based-on-dataframe-column
        alt_chart = alt.Chart(orderbook, width = 1000, height = 600).mark_bar().encode(
            x='prices',
            y='depths',
            color="side:N"
            
            )
        

        st_canvas.altair_chart(alt_chart, theme="streamlit")


        vp = ob.trades.groupby(['price','side'])['size'].sum().reset_index()
        vp.columns = ['price', 'side', 'volume']

        alt_chart2 = alt.Chart(vp, width = 1000, height = 600).mark_bar().encode(
            x='price',
            y='sum(volume)',
            color="side:N"
            )
        

        rule = alt.Chart(ob.trades).mark_rule(color='blue').encode(
            y='mean(wheat):Q'
        )
        
        base = alt.Chart(vp)
        bar_args = {'opacity': 1, 'binSpacing': 0}

        right_hist = base.mark_bar(**bar_args).encode(
            alt.X('volume:Q',
                bin=alt.Bin(maxbins=20),
                stack=None,
                title='',
                ),
            alt.Y('price', stack=True, title='', scale=alt.Scale(domain=[]),),
            alt.Color('side:N'),
        ).properties(width=1000, height=600)

        st_vp.altair_chart(right_hist, theme="streamlit")

        st_trade_log.dataframe(ob.trades, width=1000, height=600)
        time.sleep(1)


