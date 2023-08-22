var ws = require('ws');
const redis = require('redis');
var config  = require('./config');


// set up redis publisher
const publisher = redis.createClient({
    socket: {
        port: config.redisPort,
        host: config.redisHost,
    }
});
publisher.connect();
console.log("connected to redis")


var conns = [
    {   
        name: "binance_usdm_liq",
        url: 'wss://fstream.binance.com/stream?streams=!forceOrder@arr',
        on_open: {},
        on_message: async function (e) {
            if (typeof e.data === 'string') {
                var j = JSON.parse(e.data);
                var ticker = j.data.o.s;
                var price = parseFloat(j.data.o.p, 4);
                var amount = parseFloat(j.data.o.q, 4) * price;
                var side = ((j.data.o.S == 'BUY') ? 'Short' : 'Long');
                var t = j.data.o.T
                var msg = {
                    ticker: ticker,
                    amount: amount,
                    side: side,
                    price: price,
                    ts: t,
                    exch: "BINANCE"
                }
                console.log("Received from binance: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount));
                await publisher.publish('channel:binance_test', JSON.stringify(msg));
                return false;
            }
        }
    },
    {
        name: "okx_usd_swap",
        url: 'wss://ws.okx.com:8443/ws/v5/public?event=subscribe?channel=liquidation-orders?instType=SWAP',
        on_open: {
            "op": "subscribe",
            "args": [{"channel": "liquidation-orders", "instType": "SWAP"}],
        },
        on_message: async function (e) {
            var j = JSON.parse(e.toString());
            if (j.event  != 'subscribe') {
                var ticker = j.data[0].uly;
                var price = parseFloat(j.data[0].details[0].bkPx, 4);
                var amount = parseFloat(j.data[0].details[0].sz, 4) * price;
                var side = ((j.data[0].details[0].side == 'BUY') ? 'Short' : 'Long');
                var t = j.data[0].details[0].ts
                var msg = {
                    ticker: ticker,
                    amount: amount,
                    side: side,
                    price: price,
                    ts: t,
                    exch: "OKX"
                }
                console.log("Received from okx: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount));
                await publisher.publish('channel:okx_test', JSON.stringify(msg));
                return false;
            }
        }
    }
]

let connections = []

conns.map(connect);

async function connect(item) {
    var client = new ws(item.url);
    client.on('error', function () {
        console.log('Connection Error');
        client.close()
    });

    client.on('open', function () {
        console.log('WebSocket Client Connected to', item.name);
        connections.push(client)
        if (item.name != "binance_usdm_liq") {
            client.send(JSON.stringify(item.on_open))
        }
    });

    client.on('close', function () {
        console.log(item.name, 'Client Closed... reconnecting...');
        setTimeout(function() {
            connect(item);
          }, 1000);
    });

    client.on('message', item.on_message);

    setTimeout(function() {
        client.ping();
      }, 15000);

}

