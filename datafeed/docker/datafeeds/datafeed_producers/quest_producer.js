const { Sender } = require("@questdb/nodejs-client");
const redis = require('redis');

// This producer is responsible for pulling data from redis topics and pushing it to QuestDB

// Flush buffer every 500ms
const refresh_buffer_rate = 500;
const quest_host = process.env.QUEST_URL;
const quest_port = 9009;
const redis_host = process.env.REDIS_URL;
const redis_port = 6379;
const channel = "liqs:binance";
const bufferSize = 4096;

async function addMsg(sender, msg) {
    // QuestDB Sender object creation
    console.log("PRODUCER: ", msg.ticker);
    sender.table("binance_liquidations")
        .symbol("ticker", msg.ticker)
        .symbol("side", msg.side)
        .symbol("exch", msg.exch)
        .floatColumn("amount", msg.amount)
        .floatColumn("price", msg.price).atNow();
}
async function run() {
    const sender = new Sender({ bufferSize: bufferSize, log: 'error' });
    await sender.connect({ port: quest_port, host: quest_host });
    const subscriber = redis.createClient({
        socket: {
            port: redis_port,
            host: redis_host,
        }
    }).on('error', function (err) {
        console.log(err);
        subscriber = redis.createClient({
            socket: {
                port: redis_port,
                host: redis_host,
            }
        })
    });

    await subscriber.connect();
    console.log("----- QUEST PRODUCER -----");
    await subscriber.pSubscribe(channel, async (message) => {
        // receive message and create Quest Sender object using Table Definition
        var msg = JSON.parse(message);
        await addMsg(sender, msg);
    });
    setInterval(async function post_msg() {
        sender.flush().then((result) => {
            if (result == true) {
                console.log("PRODUCER: FLUSHED BUFFER")
            }
        }).catch((error) => {
            console.log(error);
        })
    }, refresh_buffer_rate);
}


run().then(value => console.log(value)).catch(err => console.log(err));