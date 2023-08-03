from cryptofeed import FeedHandler
from cryptofeed.backends.kafka import BookKafka, TradeKafka
from cryptofeed.defines import L2_BOOK, TRADES, L3_BOOK
from cryptofeed.exchanges import Coinbase, Binance, Bitfinex

feed_dict = {
    Bitfinex : {
        'max_depth': 25,
        'channels': [TRADES, L2_BOOK],
        'symbols': ['ETH-USD'],
    },
    Coinbase : {
        'max_depth': 25,
        'channels': [TRADES, L2_BOOK],
        'symbols': ['ETH-USD'],
    }
}

def main():
    f = FeedHandler()
    HOSTNAME = 'broker:29092'
    cbs = {TRADES: TradeKafka(bootstrap_servers=HOSTNAME), L2_BOOK: BookKafka(bootstrap_servers=HOSTNAME)}

    for exchange, params in feed_dict.items():
        f.add_feed(exchange(max_depth=params['max_depth'], channels=params['channels'], symbols=params['symbols'], callbacks=cbs))
    # # Add trade and lv 2 bitcoin data to Feed
    # f.add_feed(Bitfinex(max_depth=25, channels=[TRADES, L2_BOOK], symbols=['BTC-USD'], callbacks=cbs))
    # # f.add_feed(Binance(max_depth=25, channels=[TRADES, L2_BOOK], symbols=['BTC-BUSD'], callbacks=cbs))
    
    # # Example of how to extract level 3 order book data
    # # f.add_feed(Coinbase(max_depth=25, channels=[TRADES, L2_BOOK], symbols=['BTC-USD'], callbacks=cbs))

    f.run()


if __name__ == '__main__':
    main()