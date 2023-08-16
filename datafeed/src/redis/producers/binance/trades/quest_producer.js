const { Sender } = require("@questdb/nodejs-client");
const redis = require('redis');

const refresh_buffer_rate = 10000;
const quest_host = "provider.bdl.computer";
const quest_port = 31399;
const redis_host = "provider.bdl.computer";
const redis_port = 30798;
const channel = "trades:binance_btc";
const bufferSize = 10000;

async function addMsg(sender, msg) {
    console.log("ingesting", msg.ticker, "trade");
    sender.table("binance_trades_btc")
        .symbol("ticker", msg.ticker)
        .symbol("side", msg.side)
        .symbol("exch", msg.exch)
        .floatColumn("amount", msg.amount)
        .floatColumn("price", msg.price)
        .booleanColumn("mm", msg.mm)
        .intColumn("ts", msg.last_trade - msg.first_trade)
        .atNow();
}
async function run() {
    const sender = new Sender({ bufferSize: bufferSize, log: 'error' });
    await sender.connect({ port: quest_port, host: quest_host });
    const subscriber = redis.createClient({
        socket: {
            port: redis_port,
            host: redis_host,
        }
    });

    await subscriber.connect();
    await subscriber.pSubscribe(channel, async (message) => {
        var msg = JSON.parse(message);
        await addMsg(sender, msg);
    });
    setInterval(async function post_msg() {
        sender.flush().then((result) => {
            if (result == true) {
                console.log("flushed buffer")
            }
        }).catch((error) => {
            console.log(error);
        })
    }, refresh_buffer_rate);
}


run().then(value => console.log(value)).catch(err => console.log(err));