var W3CWebSocket = require('websocket').w3cwebsocket;
// This is responsible for connecting to a data source and sending data through redis
// Currently this uses a websocket and pushes to the specified redis topic
var ws = new W3CWebSocket('wss://fstream.binance.com/stream?streams=!forceOrder@arr');
const redis = require('redis');
const config = {
    min_amount: 500,
    redis_port: 6379,
    redis_host: process.env.REDIS_URL,
    redis_topic: 'liqs:binance'
}
var buf = [];
var re = redis.RedisClientType;

ws.onerror = function() {
    console.log('Connection Error');
};

ws.onopen = function() {
    console.log("----- WEBSOCKET CONSUMER -----");
};

ws.onclose = function() {
    console.log('CONSUMER: Client Closed');
};

ws.onmessage = async function(e) {
    const publisher = redis.createClient({socket: {
        port: config.redis_port,
        host: config.redis_host,
      }});
      publisher.on('error', err => console.error('client error', err));
    await publisher.connect()
    if (typeof e.data === 'string') {
        var j = JSON.parse(e.data);
        var msg = {
            ticker: j.data.o.s,
            amount: parseFloat(j.data.o.q,4 ) * parseFloat(j.data.o.p, 4),
            side: ((j.data.o.S == 'BUY') ? 'Short' : 'Long'),
            price: parseFloat(j.data.o.p, 4),
            ts: j.data.o.T,
            exch: "BINANCE"
        }
        
        if (msg.amount > config.min_amount) {
            buf.push(JSON.stringify(msg));
            console.log("CONSUMER: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount));
    }
}
setInterval(async () => {
    
    while (buf.length > 0) {
        try {
            await publisher.publish(config.redis_topic, buf.shift());
        } catch (err) {
            console.error('publish error', err);
        }
    }
}, 5000);

};



