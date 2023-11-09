const { Sender } = require("@questdb/nodejs-client");
const redis = require('redis');

// This producer is responsible for pulling data from redis topics and pushing it to QuestDB

const config = {
    quest_host: process.env.QUEST_URL,
    quest_port: process.env.QUEST_PORT,
    redis_host: process.env.REDIS_URL,
    redis_port: process.env.REDIS_PORT,
    redis_password: process.env.REDIS_PASSWORD,
    redis_channel: process.env.REDIS_CHANNEL,
    refresh_buffer_rate: 500,
    bufferSize: 4096
}

// const config = {
//     quest_host: '24.144.80.103',
//     quest_port: 9009,
//     redis_port: 25061,
//     redis_host: 'datafeeds-redis-do-user-15063471-0.c.db.ondigitalocean.com',
//     redis_password: 'AVNS_FLTYvrLh1YVC96siJlh',
//     redis_channel: 'liqs:binance',
//     refresh_buffer_rate: 500,
//     bufferSize: 4096
// }


const tableConfig = {
    name: 'binance_liquidations',
    columns: [
        { name: 'ticker', type: 'string' },
        { name: 'side', type: 'string' },
        { name: 'amount', type: 'float' },
        { name: 'price', type: 'float' },
        { name: 'exch', type: 'string' },
    ]
}

async function addMsg(sender, msg) {
    // QuestDB Sender object creation
    console.log("PRODUCER: ", msg.ticker);
    sender.table(tableConfig.name)
        .symbol("ticker", msg.ticker)
        .symbol("side", msg.side)
        .symbol("exch", msg.exch)
        .floatColumn("amount", msg.amount)
        .floatColumn("price", msg.price).atNow();
}
async function run() {
    const sender = new Sender({ bufferSize: config.bufferSize, log: 'error' });
    await sender.connect({ port: config.quest_port, host: config.quest_host });
    console.log("----- QUEST PRODUCER CONNECTED     -----");
    const subscriber = redis.createClient({
        password: config.redis_password,
        socket: {
            tls: true,
            rejectUnauthorized: false,
            port: config.redis_port,
            host: config.redis_host,
        }
    }).on('error', function (err) {
        console.log(err)

    });

    await subscriber.connect();
    console.log("----- QUEST PRODUCER STARTED   -----");
    await subscriber.pSubscribe(config.redis_channel, async (message) => {
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
            console.log(error)
        })
    }, config.refresh_buffer_rate);
}


run().then(value => console.log(value)).catch(err => console.log(err));