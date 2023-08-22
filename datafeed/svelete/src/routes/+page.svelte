<script lang="ts">
	import { io } from 'socket.io-client';
	import type { TableSource } from '@skeletonlabs/skeleton';
	import { tableMapperValues } from '@skeletonlabs/skeleton';
	import { Avatar, Paginator, CodeBlock } from '@skeletonlabs/skeleton';
	import {
		// Utilities
		createDataTableStore,
		dataTableHandler,
		// Svelte Actions
		tableInteraction,
		tableA11y
	} from '@skeletonlabs/skeleton';

	let liq: {
		ticker: string;
		amount: number;
		side: string;
		price: number;
		ts: EpochTimeStamp;
	}[] = [];

	const addLiq = (item) => {
		liq = [item, ...liq];
		liqTableStore.updateSource(liq);
	};

	const socket = io();
	console.log('created client');
	socket.on('eventFromServer', (message) => {
		console.log(message);
	});
	socket.on('liq', (message) => {
		addLiq(message);
	});

	const liqTableStore = createDataTableStore(liq, {
		// The current search term.
		search: '',
		// The current sort key.
		sort: '',
		// Paginator component settings.
		pagination: { offset: 0, limit: 10, size: 0, amounts: [1, 2, 5, 10] }
	});
	liqTableStore.subscribe((model) => {
		dataTableHandler(model);
	});



</script>

<body>
	<!-- liq tape -->
	<section class="card variant-glass">
		<!-- Search Input -->
		<div class="card-header">
			<input
				class="input"
				bind:value={$liqTableStore.search}
				type="search"
				placeholder="Search Table..."
			/>
		</div>
		<!-- Table -->
		<div class="p-4">
			<div class="table-container">
				<!-- prettier-ignore -->
				<table class="table table-hover" role="grid" use:tableInteraction use:tableA11y>
                <thead on:click={(e) => { liqTableStore.sort(e) }} on:keypress>
                    <tr>
                        <!-- <th><input type="checkbox" on:click={(e) => { liqTableStore.selectAll(e.currentTarget.checked) }} /></th> -->
                        <th data-sort="ts">Timestamp</th>
                        <th data-sort="ticker">Ticker</th>
                        <th data-sort="side">Side</th>
                        <th data-sort="amount">Amount</th>
                        <th data-sort="price">Price</th>
                        <th class="table-cell-fit"></th>
                    </tr>
                </thead>
                <tbody>
                    {#each $liqTableStore.filtered as row, rowIndex}
                        <tr aria-rowindex={rowIndex + 1}>
                            <!-- <td role="gridcell" aria-colindex={1} tabindex="0">
                                <input type="checkbox" bind:checked={row.dataTableChecked} />
                            </td> -->
                            <td role="gridcell" aria-colindex={2} tabindex="0">
                                <em class="opacity-50">{new Date(row.ts).toLocaleTimeString("en-US")}</em>
                            </td>
                            <td role="gridcell" aria-colindex={4} tabindex="0" class="md:!whitespace-normal capitalize">
                                {row.ticker}
                            </td>
                            <td role="gridcell" aria-colindex={5} tabindex="0" class="md:!whitespace-normal">
                                {row.side}
                            </td>
                            <td role="gridcell" aria-colindex={6} tabindex="0" class="md:!whitespace-normal">
                                {row.amount}
                            </td>
                            <td role="gridcell" aria-colindex={7} tabindex="0" class="md:!whitespace-normal">
                                {row.price}
                            </td>
                            <!-- <td role="gridcell" aria-colindex={6} tabindex="0" class="table-cell-fit">
                                <button class="btn variant-ghost-surface btn-sm" on:click={()=>{console.log(row,rowIndex)}}>Console Log</button>
                            </td> -->
                        </tr>
                    {/each}
                </tbody>
            </table>
			</div>
		</div>
		<div class="card-footer">
			<Paginator bind:settings={$liqTableStore.pagination} />
		</div>
	</section>
</body>
