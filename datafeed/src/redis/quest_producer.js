const { Sender } = require("@questdb/nodejs-client");
const redis = require('redis');

async function addMsg(sender, msg){
    console.log("ingesting", msg.ticker, "liquidation");
    sender.table("binance_liquidations").symbol("ticker", msg.ticker)
        .symbol("side", msg.side).symbol("exch", msg.exch)
        .floatColumn("amount", msg.amount).floatColumn("price", msg.price).atNow();
}
async function run() {
    const sender = new Sender({ bufferSize: 4096, log: 'error' });
    await sender.connect({ port: 31399, host: "provider.bdl.computer" });
    const subscriber = redis.createClient({
        socket: {
            port: 30798,
            host: "provider.bdl.computer",
        }
    });

    await subscriber.connect();
    await subscriber.pSubscribe('channel:test', async (message) => {
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
    }, 1000);
}


run().then(value => console.log(value)).catch(err => console.log(err));