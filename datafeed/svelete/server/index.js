import express from 'express'
import { createServer } from 'http'
import { Server } from 'socket.io'
import { createClient } from 'redis'
import { handler } from '../build/handler.js'


const port = 3000
const redis_host = "provider.bdl.computer"
const redis_port = 30798
const channel = "liqs:binance"

const app = express()
const server = createServer(app)
const io = new Server(server)
console.log("hi")
const subscriber = createClient({
  socket: {
    port: redis_port,
    host: redis_host,
  }
}).on('error', function (err) {
  console.log(err)
})

io.on('connection', (socket) => {
  
  socket.emit('eventFromServer', 'subscribing to feed')
  socket.emit('eventFromServer', 'connecting..')
  subscriber.connect().catch(err => console.log(err))
  run(socket, subscriber).then(value => console.log(value)).catch(err => console.log(err))

})


const refresh_buffer_rate = 1000
const quest_host = "provider.bdl.computer"
const quest_port = 31399

const bufferSize = 4096

async function run(socket, subscriber) {


  // await subscriber.connect()
  console.log("connected to redis")
  await subscriber.pSubscribe(channel, async (message) => {
    var msg = JSON.parse(message)
    socket.emit('liq', msg)
  })
}




// SvelteKit should handle everything else using Express middleware
// https://github.com/sveltejs/kit/tree/master/packages/adapter-node#custom-server
app.use(handler)

server.listen(port)
