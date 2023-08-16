var W3CWebSocket = require('websocket').w3cwebsocket;

var client = new W3CWebSocket('wss://fstream.binance.com/stream?streams=btcusdt@aggTrade');
const redis = require('redis');

function parse(data){
    var j = JSON.parse(data);
    var msg = {
        ticker: j.data.s,
        amount: parseFloat(j.data.q,4 ) * parseFloat(j.data.p, 4),
        side: ((j.data.S == 'BUY') ? 'Short' : 'Long'),
        price: parseFloat(j.data.p, 4),
        first_trade: j.data.f,
        last_trade: j.data.l,
        mm: j.data.m,
        ts: j.data.T,
        exch: "BINANCE"
    }
    if (msg.amount > 10000) {
        console.log("Received from binance: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount), JSON.stringify(msg.mm));
    }
    return msg;
};

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
    const publisher = redis.createClient({socket: {
        port: 30798,
        host: "provider.bdl.computer",
      }});
    await publisher.connect()
    if (typeof e.data === 'string') {
        var msg = parse(e.data);
        await publisher.publish('trades:binance_btc', JSON.stringify(msg));
    }

};