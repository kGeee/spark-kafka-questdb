import dask.dataframe as dd
import plotly.express as px
import streamlit as st
import pandas as pd
import time
from datetime import date, timedelta
import requests, json

def get_latest_ts():
    resp = requests.get(f"http://localhost:1337/latestTs", data={})
    
    try:
        r = json.loads(resp.text)
        return r['dataset'][0][0]
    except KeyError:
        return "2023-08-10T00:41:54.000000Z"

@st.cache_data(ttl=3)
def hit_endpoint(endpoint, data={}):
    resp = requests.get(f"http://localhost:1337/{endpoint}", data=data)
    r = json.loads(resp.text)
    df = pd.DataFrame(r["dataset"], columns=[i["name"] for i in r["columns"]])
    return df

def all_trades():
    result = hit_endpoint("query/all")
    fig = px.scatter(
        result,
        x="timestamp",
        y="amount",
        color="ticker",
        size="amount",
        title="Liquidation Data",
        width=850
    )
    st.plotly_chart(fig)


def one_hour_sampled():
    sampled_hour = hit_endpoint("query/sampled15m")
    st.plotly_chart(
        px.bar(sampled_hour, x="ticker", y="sum", width=1500),
        title="Total Liquidation Data (sampled hourly)",
    )


def liq_lookback():
    tf = st.selectbox("Timeframe", options=["15m", "1h", "12h", "24h"])
    if tf == "15m":
        df_last_hour = hit_endpoint("liqsMinutely/{}".format(tf))
    else:
        df_last_hour = hit_endpoint("liqsHourly/{}".format(tf))
    color_discrete_map = {'Long':'#73efff', 
                          'Short':'#0068c9'}
    st.plotly_chart(
        px.bar(
            df_last_hour,
            x="ticker",
            y=["sum", "side"],
            color="side",
            title=f"Total Liquidation last {tf}",
            width=850,
            color_discrete_map=color_discrete_map)
    )


def liq_progress(threshold=1000000):
    df = hit_endpoint("query/amountLiqd")
    try: longs_liqd = int(df[df["side"] == "Long"]["sum"][1])
    except KeyError: longs_liqd = 0
    try: shorts_liqd = int(df[df["side"] == "Short"]["sum"][0])
    except KeyError: shorts_liqd = 0
    col1, col2 = st.columns(2)
    col1.metric("Longs liqd", f"${int(longs_liqd)}")
    col2.metric("Shorts liqd", f"${int(shorts_liqd)}")
    st.progress((longs_liqd % threshold) / threshold, text="longs liqd")
    st.progress((shorts_liqd % threshold) / threshold, text="shorts liqd")


def liq_count_and_amount():
    liq_count_amount = hit_endpoint("query/liqCountAmount")
    liq_count, liq_amount = (
        liq_count_amount[["count", "side", "timestamp"]],
        liq_count_amount[["sum", "side", "timestamp"]],
    )
    color_discrete_map = {'Long':'#73efff', 
                          'Short':'#0068c9'}
    liq_count_tab, liq_amount_tab = st.tabs(["Count", "Amount"])
    with liq_count_tab:
        st.plotly_chart(
            px.bar(
                liq_count,
                x="timestamp",
                y=["count", "side"],
                color="side",
                title="Liquidation Count",
                width=900,
                color_discrete_map=color_discrete_map
            )
        )
    with liq_amount_tab:
        st.plotly_chart(
            px.bar(
                liq_amount,
                x="timestamp",
                y=["sum", "side"],
                color="side",
                title="Liquidation Amount",
                width=900,
                color_discrete_map=color_discrete_map
            )
        )


def liq_count_and_amount_ticker(ticker):
    liq_count_amount = hit_endpoint(f"tickerLiqCountAmount/{ticker}")
    liq_count, liq_amount = (
        liq_count_amount[["count", "side", "timestamp"]],
        liq_count_amount[["sum", "side", "timestamp"]],
    )

    liq_count_amount["timestamp"] = pd.to_datetime(
        liq_count_amount["timestamp"].astype(str)
    ).dt.strftime("%m/%d/%Y %H:%M:%S")
    st.dataframe(liq_count_amount[::-1], width=1500)

    st.plotly_chart(
        px.bar(
            liq_count,
            x="timestamp",
            y=["count", "side"],
            color="side",
            width=1500,
            height=500,
            title=f"Liquidation Count {ticker}",
        )
    )
    st.plotly_chart(
        px.bar(
            liq_amount,
            x="timestamp",
            y=["sum", "side"],
            color="side",
            width=1500,
            height=500,
            title=f"Liquidation Amount {ticker}",
        )
    )


def liq_log():
    df = hit_endpoint("query/log")

    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none;}
                thead tr th {font-size: 15px; font-weight:20; color: white !important;}
                tbody th {display:none;}
                table { border-collapse:collapse; }
                th {text-align: center; background-color: #1B91F8;}
                td { border-style : hidden!important; }
                </style>
                """
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    st.table(df)


def main():
    st.set_page_config(page_title="Liquidations - Binance Alts", layout="wide")

    if not "sleep_time" in st.session_state:
        st.session_state.sleep_time = 5

    if not "auto_refresh" in st.session_state:
        st.session_state.auto_refresh = True

    auto_refresh = True
    st.session_state.sleep_time = 3

    if not "latestTs" in st.session_state:
        st.session_state.latestTs = get_latest_ts()

    liq_progress()

    col1, col2 = st.columns(2)
    with col1: all_trades()
    with col2: liq_log()

    col3, col4 = st.columns(2)

    with col3: liq_lookback()
    with col4: liq_count_and_amount()

    one_hour_sampled()

    ticker = st.text_input("ticker", value="ETH")
    liq_count_and_amount_ticker(ticker)

    while auto_refresh:
        ts = get_latest_ts()
        if st.session_state.latestTs != ts:
            # print(st.session_state.latestTs, ts)
            st.session_state.latestTs = ts
            st.experimental_rerun()
        else:
            time.sleep(st.session_state.sleep_time)



if __name__ == "__main__":
    main()
