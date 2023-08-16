var W3CWebSocket = require('websocket').w3cwebsocket;

async function run() {
    const redis = require('redis');
    const publisher = redis.createClient({
        socket: {
            port: 30798,
            host: "provider.bdl.computer",
        }
    });
    await publisher.connect()

    var client = new W3CWebSocket('wss://fstream.binance.com/stream?streams=!forceOrder@arr');

    client.onerror = function () {
        console.log('Connection Error');
    };

    client.onopen = function () {
        console.log('WebSocket Client Connected');
        

    };

    client.onclose = function () {
        console.log('echo-protocol Client Closed');
    };

    client.onmessage = async function (e) {
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
            await publisher.publish('channel:test', JSON.stringify(msg));
        }

    };
}
run().then(value => console.log(value)).catch(err => console.log(err));