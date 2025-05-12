<script lang="ts">	
	import SvelteMarkdown from 'svelte-markdown'

	import Highlight from "svelte-highlight";	
	import _3024 from "svelte-highlight/styles/3024";

	// direct import (recommended)
	import python from 'svelte-highlight/languages/python';

	import FileUpload from './FileUpload.svelte';

	// Mock threads
	let threads = [
		{ id: 1, title: 'RFM Bubble Chart', lastQuery: 'Show a bubble chart of customer segments', lastUpdated: '2h ago' },
		{ id: 2, title: 'RFM Heatmap', lastQuery: 'Show a heatmap of RFM scores', lastUpdated: '1d ago' },
	];
	let selectedThread = threads[0];

	let selectedFile: string | null = null;
	let uploadedFiles: string[] = [];
	let analysisQuery = '';
	let loading = false;
	let error: string | null = null;
	let result: any = null;
	let analysisResult: any = null;
	let chart_explanation: string | null = null; // Explanation of the chart
	let code_explanation: string | null = null; // Explanation of the code
	let chartData: string | null = null; // Base64 encoded image data
	let pythonCode: string | null = null; // Python code for the chart
	let isChart: boolean = false; // Flag to indicate if the response is a chart

	async function handleFileUpload(event: CustomEvent<{ filename: string }>) {
		selectedFile = event.detail.filename;
		if (!uploadedFiles.includes(selectedFile)) {
			uploadedFiles = [...uploadedFiles, selectedFile];
		}
	}

	function selectFile(file: string) {
		selectedFile = file;
	}

	function selectThread(thread: any) {
		selectedThread = thread;
		// Reset state for demo
		result = null;
		chartData = null;
		pythonCode = null;
		isChart = false;
		chart_explanation = null;
		code_explanation = null;
		error = null;
		analysisQuery = '';
	}

	async function handleAnalysisSubmit() {
		if (!selectedFile || !analysisQuery) {
			error = 'Please select a file and enter your analysis query';
			return;
		}

		loading = true;
		error = null;
		result = null;
		analysisResult = null;

		try {
			const response = await fetch('http://localhost:5000/api/analyze', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					filename: selectedFile,
					query: analysisQuery
				})
			});

			if (!response.ok) {
				throw new Error('Failed to generate analysis');
			}
			
			const data = await response.json();
			analysisResult = data.data;
			console.log('analysisResult', analysisResult);
			
			// Update thread with new analysis
			const newThread = {
				id: threads.length + 1,
				title: analysisQuery.slice(0, 30) + (analysisQuery.length > 30 ? '...' : ''),
				lastQuery: analysisQuery,
				lastUpdated: 'Just now'
			};
			threads = [newThread, ...threads];
			selectedThread = newThread;
			
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to generate analysis';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
  {@html _3024}
</svelte:head>
<div class="analysis-layout">
	<aside class="analysis-sidebar">
		<div class="sidebar-header">Analysis Threads</div>
		<ul class="thread-list">
			{#each threads as thread}
				<button type="button" class="thread-item {thread.id === selectedThread.id ? 'active' : ''}" on:click={() => selectThread(thread)}>
					<div class="thread-title">{thread.title}</div>
					<div class="thread-meta">{thread.lastQuery}</div>
					<div class="thread-time">{thread.lastUpdated}</div>
				</button>
			{/each}
		</ul>
	</aside>

	<div class="analysis-main">
		<div class="analysis-header">
			<h1>{selectedThread.title}</h1>
		</div>

		<div class="analysis-content">
			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			{#if analysisResult}
				<div class="result-section">
					{#if analysisResult.code_blocks && analysisResult.code_blocks.length > 0}
						<div class="code-card">
							<h3>Python Code</h3>
							{#each analysisResult.code_blocks as codeBlock}
								<Highlight langtag language={python} code={codeBlock.code} />
							{/each}
						</div>
					{/if}

					{#if analysisResult.explanations && analysisResult.explanations.length > 0}
						{#each analysisResult.explanations as explanation}
							<div class="code-card">
								<h3>{explanation.type.charAt(0).toUpperCase() + explanation.type.slice(1)} Explanation</h3>
								<div class="chart-description">
									<SvelteMarkdown source={explanation.text} />
								</div>
							</div>
						{/each}
					{/if}

					{#if analysisResult.visualizations && analysisResult.visualizations.length > 0}
						{#each analysisResult.visualizations as visualization}
							<div class="chart-card">
								<h3>{visualization.title}</h3>
								<img src={visualization.data.url || `data:image/png;base64,${visualization.data.image}`} alt={visualization.title} />
								{#if visualization.description}
									<SvelteMarkdown source={visualization.description} />
								{/if}
							</div>
						{/each}
					{/if}

					{#if analysisResult.data_tables && analysisResult.data_tables.length > 0}
						{#each analysisResult.data_tables as table}
							<div class="table-card">
								<h3>{table.title || 'Data Table'}</h3>
								{#if table.description}
									<p class="table-description">{table.description}</p>
								{/if}
								<table>
									<thead>
										<tr>
											{#each table.headers as header}
												<th>{header}</th>
											{/each}
										</tr>
									</thead>
									<tbody>
										{#each table.data as row}
											<tr>
												{#each table.headers as header}
													<td>{row[header]}</td>
												{/each}
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						{/each}
					{/if}
				</div>
			{/if}
		</div>

		<!-- Fixed bottom input bar -->
		<div class="analysis-bottom-bar">
			<div class="file-chips">
				{#each uploadedFiles as file}
					<button type="button" class="file-chip {file === selectedFile ? 'active' : ''}" on:click={() => selectFile(file)}>
						{file}
					</button>
				{/each}
			</div>
			<FileUpload on:uploadComplete={handleFileUpload} />
			<textarea
				bind:value={analysisQuery}
				placeholder="Type your analysis query..."
				rows="2"
				class="bottom-query"
			></textarea>
			<button
				on:click={handleAnalysisSubmit}
				disabled={!selectedFile || !analysisQuery || loading}
				class="submit-btn"
			>
				{loading ? 'Generating...' : 'Generate'}
			</button>
		</div>
	</div>
</div>

<style>
	.analysis-layout {
		display: flex;
		height: 100vh;
		background: #f7f8fa;
	}

	.analysis-sidebar {
		width: 270px;
		background: #fff;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
	}

	.sidebar-header {
		font-weight: 700;
		font-size: 1.1rem;
		padding: 1.5rem 1rem 1rem 1rem;
		color: #222;
		border-bottom: 1px solid #e0e0e0;
	}

	.thread-list {
		list-style: none;
		padding: 0;
		margin: 0;
		flex: 1;
		overflow-y: auto;
	}

	.thread-item {
		padding: 1rem 1rem 0.75rem 1rem;
		border: none;
		background: none;
		text-align: left;
		width: 100%;
		cursor: pointer;
		transition: background 0.2s;
		border-bottom: 1px solid #f0f0f0;
	}
	.thread-item.active, .thread-item:hover {
		background: #f0f4ff;
	}
	.thread-title {
		font-weight: 600;
		color: #1e40af;
	}
	.thread-meta {
		font-size: 0.95rem;
		color: #666;
		margin-top: 0.2rem;
	}
	.thread-time {
		font-size: 0.8rem;
		color: #aaa;
		margin-top: 0.1rem;
	}

	.analysis-main {
		flex: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		position: relative;
	}

	.analysis-header {
		padding: 2rem 2rem 1rem 2rem;
	}
	.analysis-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: #222;
		margin: 0;
	}

	.analysis-content {
		flex: 1;
		overflow-y: auto;
		padding: 0 2rem 7rem 2rem;
	}

	.result-section {
		display: flex;
		flex-direction: column;
		gap: 2rem;
		margin-top: 2rem;
		flex-wrap: wrap;
	}

	.code-card, .chart-card {
		background: #f9fafb;
		border-radius: 8px;
		box-shadow: 0 1px 4px rgba(0,0,0,0.04);
		padding: 1.5rem;
		flex: 1 1 350px;
		min-width: 320px;
	}
	.code-card h3, .chart-card h3 {
		margin-top: 0;
		font-size: 1.1rem;
		color: #222;
	}
	.chart-card img {
		max-width: 100%;
		height: auto;
		border-radius: 6px;
		margin-top: 1rem;
		background: #fff;
		box-shadow: 0 1px 4px rgba(0,0,0,0.04);
	}

	.analysis-bottom-bar {
		position: fixed;
		bottom: 0;
		/* left: 270px; */
		/* right: 0; */
		border-radius: 20px;
		background: #cacaca;
		border-top: 1px solid #e0e0e0;
		padding: 1rem 2rem;
		display: flex;
		align-items: flex-end;
		gap: 1rem;
		z-index: 10;
	}
	.file-chips {
		display: flex;
		gap: 0.5rem;
		flex-wrap: wrap;
	}
	.file-chip {
		background: #f0f1f5;
		color: #333;
		padding: 0.4rem 1rem;
		border-radius: 16px;
		font-size: 0.95rem;
		cursor: pointer;
		transition: background 0.2s;
		border: 1px solid #e0e0e0;
	}
	.file-chip.active {
		background: #e0e7ff;
		color: #1e40af;
		border: 1px solid #6366f1;
	}
	.bottom-query {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #e0e0e0;
		border-radius: 6px;
		font-size: 1rem;
		resize: vertical;
		background: #f9fafb;
		color: #222;
		min-width: 200px;
		max-width: 600px;
	}
	.submit-btn {
		padding: 0.75rem 1.5rem;
		background-color: #6366f1;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: background 0.2s;
	}
	.submit-btn:disabled {
		background: #d1d5db;
		color: #888;
		cursor: not-allowed;
	}
	.error-message {
		color: #b91c1c;
		background: #fef2f2;
		padding: 0.75rem 1rem;
		border-radius: 6px;
		margin-top: 1rem;
	}
	@media (max-width: 900px) {
		.analysis-layout {
			flex-direction: column;
		}
		.analysis-sidebar {
			width: 100%;
			border-right: none;
			border-bottom: 1px solid #e0e0e0;
		}
		.analysis-bottom-bar {
			left: 0;
			padding: 1rem;
		}
	}
	@media (max-width: 600px) {
		.analysis-header, .analysis-content {
			padding-left: 1rem;
			padding-right: 1rem;
		}
		.analysis-bottom-bar {
			padding-left: 1rem;
			padding-right: 1rem;
		}
	}
	.table-card {
		background: #f9fafb;
		border-radius: 8px;
		box-shadow: 0 1px 4px rgba(0,0,0,0.04);
		padding: 1.5rem;
		flex: 1 1 100%;
		min-width: 320px;
		margin-top: 1rem;
	}
	.table-card table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 1rem;
		background: white;
		border-radius: 6px;
		overflow: hidden;
	}
	.table-card th, .table-card td {
		padding: 0.75rem;
		text-align: left;
		border-bottom: 1px solid #e0e0e0;
	}
	.table-card th {
		background: #f0f4ff;
		font-weight: 600;
		color: #1e40af;
	}
	.table-card tr:last-child td {
		border-bottom: none;
	}
	.chart-description, .table-description {
		margin-top: 1rem;
		color: #666;
		font-size: 0.95rem;
		line-height: 1.5;
	}
</style>
