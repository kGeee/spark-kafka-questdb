const redis = require('redis');
const axios = require('axios');
var config  = require('./producers/config');

(async () => {

  const subscriber = redis.createClient({
      socket: {
          port: config.redisPort,
          host: config.redisHost,
      }
  });
  await subscriber.connect();
  await subscriber.pSubscribe('channel:*', async (message) => {
    // console.log(message); // 'message'
    var msg = JSON.parse(message);
    console.log(msg.ticker, msg.amount, msg.side, msg.exch)
    // try {
    //   var query = `insert into binance_liquidations values ('${msg.ticker}', '${msg.side}', '${msg.exch}', ${msg.amount}, ${msg.price}, systimestamp())`
    //   const response = await axios.get(`http://provider.bdl.computer:30793/exec?query=${query}`)
    //   console.log(`received from redis`);
    // } catch (error) {
    //   console.log(error);
    // }
  });

})();