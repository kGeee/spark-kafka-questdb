const { Sender } = require("@questdb/nodejs-client");
const redis = require('redis');

const subscriber = redis.createClient({socket: {
    port: 30798,
    host: "provider.bdl.computer",
  }});

async function post_msg(msg) {
    const sender = new Sender({ bufferSize: 4096 });
    await sender.connect({ port: 31399, host: "provider.bdl.computer" });
    sender.table("binance_liquidations").symbol("ticker", msg.ticker)
        .symbol("side", msg.side).symbol("exch", msg.exch)
        .floatColumn("amount", msg.amount).floatColumn("price", msg.price).atNow();
    await sender.flush();
    await sender.close();
    return new Promise(resolve => resolve(0));
}

async function run() {
    await subscriber.connect();
    await subscriber.pSubscribe('channel:*', async (message) => {
        var msg = JSON.parse(message);
        console.log("ingesting ", msg.ticker, " liquidation");
        await post_msg(msg);
    });

}

run().then(value => console.log(value)).catch(err => console.log(err));