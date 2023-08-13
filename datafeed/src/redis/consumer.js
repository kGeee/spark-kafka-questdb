const redis = require('redis');
const axios = require('axios');

(async () => {

  const subscriber = redis.createClient();
  await subscriber.connect();
  await subscriber.pSubscribe('channel:*', async (message) => {
    // console.log(message); // 'message'
    var msg = JSON.parse(message);
    try {
      var query = `insert into binance_liquidations values ('${msg.ticker}', '${msg.side}', '${msg.exch}', ${msg.amount}, ${msg.price}, systimestamp())`
      const response = await axios.get(`http://provider.bdl.computer:30793/exec?query=${query}`)
      console.log(`received from redis`);
    } catch (error) {
      console.log(error);
    }
  });

})();