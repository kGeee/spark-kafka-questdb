var base = require('./base_ws_producer');
console.log("starting ")
var config  = require('./config');



config.connections.forEach(function (item, index) {
    var run = base.run
    run(item.url, item.name).then(value => console.log(value)).catch(err => console.log(err));
  });
