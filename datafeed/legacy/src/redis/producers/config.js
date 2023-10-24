// async function binance(e) {
//     if (typeof e.data === 'string') {
//         var j = JSON.parse(e.data);
//         var ticker = j.data.o.s;
//         var price = parseFloat(j.data.o.p, 4);
//         var amount = parseFloat(j.data.o.q, 4) * price;
//         var side = ((j.data.o.S == 'BUY') ? 'Short' : 'Long');
//         var t = j.data.o.T
//         var msg = {
//             ticker: ticker,
//             amount: amount,
//             side: side,
//             price: price,
//             ts: t,
//             exch: "BINANCE"
//         }
//         console.log("Received from binance: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount));
//         await publisher.publish('channel:binance_test', JSON.stringify(msg));
//     }

// };

// async function okx(e) {
//     if (typeof e.data === 'string') {
//         var j = JSON.parse(e.data);
//         var ticker = j.data.o.s;
//         var price = parseFloat(j.data.o.p, 4);
//         var amount = parseFloat(j.data.o.q, 4) * price;
//         var side = ((j.data.o.S == 'BUY') ? 'Short' : 'Long');
//         var t = j.data.o.T
//         var msg = {
//             ticker: ticker,
//             amount: amount,
//             side: side,
//             price: price,
//             ts: t,
//             exch: "BINANCE"
//         }
//         console.log("Received from binance: ", JSON.stringify(msg.ticker), JSON.stringify(msg.amount));
//         await publisher.publish('channel:okx_test', JSON.stringify(msg));
//     }

// };



module.exports = {
    redisPort : 30798,
    redisHost : "provider.bdl.computer",
    connections : [
        {   
            name: "binance_usdm_liq",
            url: 'wss://fstream.binance.com/stream?streams=!forceOrder@arr',
        },
        {
            name: "okx_usd_swap",
            url: 'wss://ws.okx.com:8443/ws/v5/public?event=subscribe?channel=liquidation-orders?instType=SWAP'
        }
    ],

  }

 