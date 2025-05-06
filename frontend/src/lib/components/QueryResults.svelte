<script lang="ts">
	export let results: Array<Record<string, any>> = [];
	export let loading = false;
	export let error: string | null = null;
</script>

<div class="query-results">
	{#if loading}
		<div class="loading">
			<div class="typing-indicator">
				<span></span>
				<span></span>
				<span></span>
			</div>
		</div>
	{:else if error}
		<div class="error">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="24"
				height="24"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
			>
				<circle cx="12" cy="12" r="10" />
				<line x1="12" y1="8" x2="12" y2="12" />
				<line x1="12" y1="16" x2="12.01" y2="16" />
			</svg>
			<p>{error}</p>
		</div>
	{:else if results.length === 0}
		<div class="empty-state">
			<p>No results to display</p>
		</div>
	{:else}
		<div>
			{results}
		</div>
		<!-- <div class="table-container">
			<table>
				<thead>
					<tr>
						{#each Object.keys(results[0]) as header}
							<th>{header}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each results as row}
						<tr>
							{#each Object.values(row) as cell}
								<td>{cell}</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div> -->
	{/if}
</div>

<style>
	.query-results {
		color: #333333;
		font-size: 0.875rem;
		line-height: 1.5;
	}

	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
	}

	.typing-indicator {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}

	.typing-indicator span {
		width: 8px;
		height: 8px;
		background-color: #666666;
		border-radius: 50%;
		animation: typing 1s infinite ease-in-out;
	}

	.typing-indicator span:nth-child(1) {
		animation-delay: 0.2s;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: 0.3s;
	}

	.typing-indicator span:nth-child(3) {
		animation-delay: 0.4s;
	}

	@keyframes typing {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-4px);
		}
	}

	.error {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		color: #dc2626;
		padding: 1rem;
	}

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		color: #666666;
	}

	.table-container {
		overflow-x: auto;
		margin: 0.5rem 0;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.875rem;
		background-color: #ffffff;
		border-radius: 0.5rem;
		overflow: hidden;
		border: 1px solid #e0e0e0;
	}

	th,
	td {
		padding: 0.75rem 1rem;
		text-align: left;
		border-bottom: 1px solid #e0e0e0;
	}

	th {
		background-color: #f9f9f9;
		font-weight: 600;
		color: #333333;
	}

	td {
		color: #333333;
	}

	tr:last-child td {
		border-bottom: none;
	}

	tr:hover td {
		background-color: #f0f0f0;
	}
</style>
