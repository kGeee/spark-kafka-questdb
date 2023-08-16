import { localStorageStore } from '@skeletonlabs/skeleton';
import type { Writable } from 'svelte/store';

type Note = {
	id: string;
	content: string;
	tags: string[];
};

type Liquidation = {
	ticker: string;
	side: string;
	amount: number;
	price: number;
	exch: string;
}
export const liquidationStore: Writable<Liquidation[]> = localStorageStore('liquidations', []);
export const noteStore: Writable<Note[]> = localStorageStore('notes', []);
