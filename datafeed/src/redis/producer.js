// const redis = require('redis');
// const publisher = redis.createClient();



var W3CWebSocket = require('websocket').w3cwebsocket;

var client = new W3CWebSocket('wss://fstream.binance.com/stream?streams=!forceOrder@arr');
const redis = require('redis');


client.onerror = function() {
    console.log('Connection Error');
};

client.onopen = function() {
    console.log('WebSocket Client Connected');
};

client.onclose = function() {
    console.log('echo-protocol Client Closed');
};

client.onmessage = async function(e) {
    const publisher = redis.createClient();
    await publisher.connect()
    if (typeof e.data === 'string') {
        var j = JSON.parse(e.data);
        var ticker = j.data.o.s;
        var price = parseFloat(j.data.o.p, 4);
        var amount = parseFloat(j.data.o.q,4 ) * price;
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