import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

import {Server} from 'socket.io'


export const websocketServer = {
	name: 'webSocketServer',
	configureServer(server) {
		const io = new Server(server.httpServer)
		io.on('connect', (socket) => {
			socket.emit('eventFromServer', 'Hello, World!');
		})
	}
}

// run().then(value => console.log(value)).catch(err => console.log(err));


export default defineConfig({
	plugins: [sveltekit(), websocketServer],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});


