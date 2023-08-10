from cryptofeed import FeedHandler
from cryptofeed.defines import LIQUIDATIONS
from cryptofeed.backends.kafka import BookKafka, TradeKafka, LiquidationsKafka
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
    HOSTNAME = 'broker:29092'
    print("Querying exchange metadata")
    for exchange_string, exchange_class in exch.items():
        try:
            if LIQUIDATIONS in exchange_class.info()['channels']['websocket']:
                configured.append(exchange_string)
                symbols = ["BTC-USDT-SWAP","SOL-USDT-SWAP","ETH-USDT-SWAP","AAVE-USDT-SWAP","LDO-USDT-SWAP", "APT-USDT-SWAP", "BCH-USDT-SWAP", ""]
                f.add_feed(exchange_class(subscription={LIQUIDATIONS: symbols}, callbacks={LIQUIDATIONS: liquidations}))#LiquidationsKafka(bootstrap_servers=HOSTNAME)}))
        except:
            pass
    print("Starting feedhandler for exchanges:", ', '.join(configured))
    f.run()


if __name__ == '__main__':
    main()