from cryptofeed import FeedHandler
from cryptofeed.defines import LIQUIDATIONS
from cryptofeed.exchanges import EXCHANGE_MAP
from cryptofeed.exchanges import Coinbase, Binance, Bitfinex, OKX

async def liquidations(data, receipt):
    print(data)
    if float(data.quantity) > 1000:
        print(f'{receipt} Symbol: {data.symbol} Side: {data.side} Quantity: {data.quantity} Price: {data.price}')


def main():
    f = FeedHandler()
    configured = []
    exch = {"okx": OKX}
    print("Querying exchange metadata")
    for exchange_string, exchange_class in exch.items():
        try:
            if LIQUIDATIONS in exchange_class.info()['channels']['websocket']:
                configured.append(exchange_string)
                symbols = [sym for sym in exchange_class.symbols() if 'PINDEX' not in sym]
                f.add_feed(exchange_class(subscription={LIQUIDATIONS: symbols}, callbacks={LIQUIDATIONS: liquidations}))
        except:
            pass
    print("Starting feedhandler for exchanges:", ', '.join(configured))
    f.run()


if __name__ == '__main__':
    main()