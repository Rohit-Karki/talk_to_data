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
	let activeTab = 'outline'; // Add this line near the top of the script section

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
	<aside class="analysis-sidebar-left">
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

			<div class="chat-container">
				{#if analysisResult}
					<div class="message user-message">
						<div class="message-content">
							<p>{analysisQuery}</p>
						</div>
					</div>
					<div class="message assistant-message">
						<div class="message-content">
							{#if analysisResult.code_blocks && analysisResult.code_blocks.length > 0}
								<div class="code-block-card">
									<div class="code-block-header">
										<span class="python-icon">🐍</span>
										<span class="python-label">Python</span>
										<div class="code-block-actions">
											<button class="code-action-btn">Rerun code</button>
											<button class="code-action-btn">Edit code</button>
										</div>
									</div>
									<div class="code-block-content">
										{#each analysisResult.code_blocks as codeBlock}
											<Highlight langtag language={python} code={codeBlock.code} />
										{/each}
									</div>
								</div>
							{/if}

							{#if analysisResult.explanations && analysisResult.explanations.length > 0}
								{#each analysisResult.explanations as explanation}
									<div class="code-explanation-card">
										<div class="explanation-title">Code Explanation</div>
										<div class="explanation-content">
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
					</div>
				{/if}
			</div>
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

	<aside class="analysis-sidebar-right">
		<div class="tabs">
			<button 
				class="tab-button {activeTab === 'outline' ? 'active' : ''}" 
				on:click={() => activeTab = 'outline'}
			>
				Outline
			</button>
			<button 
				class="tab-button {activeTab === 'notes' ? 'active' : ''}" 
				on:click={() => activeTab = 'notes'}
			>
				Notes
			</button>
			<button 
				class="tab-button {activeTab === 'data-explorer' ? 'active' : ''}" 
				on:click={() => activeTab = 'data-explorer'}
			>
				Data Explorer
			</button>
		</div>
		<div class="tab-content">
			{#if activeTab === 'outline'}
				<div class="tab-pane">
					<h3>Analysis Outline</h3>
					<ul class="outline-list">
						{#each threads as thread}
							<li class="outline-item {thread.id === selectedThread.id ? 'active' : ''}" on:click={() => selectThread(thread)}>
								<span class="outline-title">{thread.title}</span>
								<span class="outline-time">{thread.lastUpdated}</span>
							</li>
						{/each}
					</ul>
				</div>
			{:else if activeTab === 'notes'}
				<div class="tab-pane">
					<h3>Analysis Notes</h3>
					<div class="notes-content">
						<p>Add your analysis notes here...</p>
					</div>
				</div>
			{:else if activeTab === 'data-explorer'}
				<div class="tab-pane">
					<h3>Data Explorer</h3>
					<div class="data-explorer-content">
						<p>Explore your data here...</p>
					</div>
				</div>
			{/if}
		</div>
	</aside>
</div>

<style>
	.analysis-layout {
		position: relative;
		display: flex;
		height: 95vh;
		background: #f7f8fa;
		overflow-y: scroll;
	}

	.analysis-sidebar-left {
		/* position: absolute; */
		width: 300px;
		background: #fff;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
		top: 0;
		left: 0;
		bottom: 0;
	}
	.analysis-sidebar-right {
		/* position: absolute; */
		width: 400px;
		background: #fff;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
		top: 0;
		right: 0;
		bottom: 0;
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

	.code-block-card {
		background: #181c23;
		border-radius: 12px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.10);
		padding: 0;
		margin-bottom: 1.5rem;
		overflow: hidden;
	}

	.code-block-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: #23272f;
		padding: 0.75rem 1.2rem;
		border-bottom: 1px solid #23272f;
	}

	.python-icon {
		font-size: 1.3rem;
		margin-right: 0.5rem;
	}

	.python-label {
		font-weight: 700;
		color: #ffd43b;
		font-size: 1.05rem;
		margin-right: auto;
	}

	.code-block-actions {
		display: flex;
		gap: 0.5rem;
	}

	.code-action-btn {
		background: #23272f;
		color: #bdbdbd;
		border: 1px solid #353b45;
		border-radius: 6px;
		padding: 0.3rem 0.8rem;
		font-size: 0.95rem;
		cursor: pointer;
		transition: background 0.2s;
	}
	.code-action-btn:hover {
		background: #353b45;
		color: #fff;
	}

	.code-block-content {
		padding: 1.2rem;
		background: #181c23;
		font-family: 'Fira Mono', 'Consolas', 'Menlo', monospace;
		font-size: 1rem;
		color: #e6e6e6;
		border-radius: 0 0 12px 12px;
	}

	.code-explanation-card {
		background: #23272f;
		border-radius: 10px;
		margin-top: 1rem;
		padding: 1.2rem 1.5rem;
	}

	.explanation-title {
		font-weight: 700;
		color: #fff;
		font-size: 1.08rem;
		margin-bottom: 0.5rem;
	}

	.explanation-content {
		color: #e6e6e6;
		font-size: 1rem;
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
		.analysis-sidebar-left {
			width: 100%;	
			border-right: none;
			border-bottom: 1px solid #e0e0e0;
		}
		.analysis-sidebar-right {
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
		background: #22272e;
		border-radius: 10px;
		box-shadow: 0 2px 8px rgba(0,0,0,0.08);
		padding: 1.5rem;
		margin-top: 1rem;
		overflow-x: auto;
	}
	.table-card table {
		width: 100%;
		border-collapse: separate;
		border-spacing: 0;
		background: #22272e;
		border-radius: 10px;
		overflow: hidden;
	}
	.table-card th, .table-card td {
		padding: 0.85rem 1.2rem;
		text-align: left;
	}
	.table-card th {
		background: #2d333b;
		color: #fff;
		font-weight: 700;
		border-bottom: 2px solid #444c56;
	}
	.table-card td {
		background: #22272e;
		color: #e6e6e6;
		border-bottom: 1px solid #2d333b;
	}
	.table-card tr:nth-child(even) td {
		background: #23272f;
	}
	.table-card tr:hover td {
		background: #2d333b;
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
	.tabs {
		display: flex;
		border-bottom: 1px solid #e0e0e0;
		background: #fff;
	}

	.tab-button {
		flex: 1;
		padding: 1rem;
		border: none;
		background: none;
		cursor: pointer;
		font-weight: 500;
		color: #666;
		transition: all 0.2s;
	}

	.tab-button:hover {
		background: #f0f4ff;
		color: #1e40af;
	}

	.tab-button.active {
		color: #1e40af;
		border-bottom: 2px solid #1e40af;
	}

	.tab-content {
		flex: 1;
		overflow-y: auto;
	}

	.tab-pane {
		padding: 1rem;
	}

	.tab-pane h3 {
		margin: 0 0 1rem 0;
		font-size: 1.1rem;
		color: #222;
	}

	.outline-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.outline-item {
		padding: 0.75rem;
		cursor: pointer;
		border-radius: 4px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.outline-item:hover {
		background: #f0f4ff;
	}

	.outline-item.active {
		background: #e0e7ff;
	}

	.outline-title {
		font-weight: 500;
		color: #1e40af;
	}

	.outline-time {
		font-size: 0.8rem;
		color: #666;
	}

	.notes-content, .data-explorer-content {
		color: #666;
		font-size: 0.95rem;
		line-height: 1.5;
	}

	.chat-container {
		width: 100%;
		max-width: 800px;
		margin: 0 auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.message {
		display: flex;
		margin-bottom: 1rem;
	}

	.user-message {
		justify-content: flex-end;
	}

	.assistant-message {
		justify-content: flex-start;
	}

	.message-content {
		max-width: 80%;
		padding: 1rem;
		border-radius: 12px;
		box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
	}

	.user-message .message-content {
		background-color: #6366f1;
		color: white;
		border-top-right-radius: 4px;
	}

	.assistant-message .message-content {
		background-color: #f3f4f6;
		color: #1f2937;
		border-top-left-radius: 4px;
	}

	.message-content p {
		margin: 0;
		line-height: 1.5;
	}

	.message-content p + p {
		margin-top: 0.5rem;
	}

	.assistant-message .code-block-card,
	.assistant-message .chart-card,
	.assistant-message .table-card {
		background: transparent;
		box-shadow: none;
		padding: 0;
		margin-top: 1rem;
	}

	.assistant-message .code-block-card .code-block-header,
	.assistant-message .code-block-card .code-block-content,
	.assistant-message .code-block-card .code-action-btn,
	.assistant-message .chart-card h3,
	.assistant-message .table-card h3 {
		color: #1f2937;
		font-size: 1rem;
		margin-bottom: 0.5rem;
	}

	.assistant-message .chart-card img {
		margin-top: 0.5rem;
	}

	.assistant-message .table-card table {
		margin-top: 0.5rem;
	}
</style>
