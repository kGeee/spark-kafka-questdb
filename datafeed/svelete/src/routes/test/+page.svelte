<script lang="ts">
	import Plot from 'svelte-plotly.js';

	const data = [
		{
            // x is the timestamp, y is the amount
			x: [0, 1, 2, 3,4],
			y: [3, 2, 10, 4,5],
			mode: 'markers',
			marker: {
				size: [40, 60, 80, 100, 20]
			}
		}
	];
</script>

<Plot
	{data}
	layout={{
		title: 'testing',
		margin: { t: 0 },
		showlegend: false
	}}
	fillParent="width"
	debounce={250}
/>
