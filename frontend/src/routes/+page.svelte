<script lang="ts">
	import ChatHistory from '$lib/components/ChatHistory.svelte';
	import QueryInput from '$lib/components/QueryInput.svelte';
	import QueryResults from '$lib/components/QueryResults.svelte';
	import Analysis from '$lib/components/Analysis.svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import FileUpload from '$lib/components/FileUpload.svelte';

	let activeTab = 'chat';
	let chats = [
		{
			id: '1',
			title: 'Sales Analysis',
			timestamp: '2 hours ago',
			preview: 'Show me the total sales by region'
		},
		{
			id: '2',
			title: 'Customer Insights',
			timestamp: '1 day ago',
			preview: 'What are the top 5 customers by revenue?'
		},
		{
			id: '3',
			title: 'Product Performance',
			timestamp: '3 days ago',
			preview: 'Compare product sales across categories'
		}
	];

	let results: Array<Record<string, any>> = [];
	let loading = false;
	let error: string | null = null;

	function handleChatSelect(event: CustomEvent) {
		const chat = event.detail.chat;
		goto(`/chat/${chat.id}`);
	}

	function handleTabChange(tab: string) {
		activeTab = tab;
		if (tab === 'chat') {
			goto('/');
		} else {
			goto('/analysis');
		}
	}

	async function handleQuerySubmit(event: CustomEvent) {
		const query = event.detail.query;
		loading = true;
		error = null;

		try {
			const response = await fetch('http://localhost:5000/api/query', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ question: query })
			});

			if (!response.ok) {
				throw new Error('Failed to process query');
			}

			const data = await response.json();
			results = data.generate_answer.answer;
		} catch (err) {
			error = 'Failed to process query. Please try again.';
			results = [];
		} finally {
			loading = false;
		}
	}

	function handleUploadComplete(event: CustomEvent<{ filename: string }>) {
		console.log('File uploaded:', event.detail.filename);
		// You can add additional logic here after successful upload
	}
</script>

<svelte:head>
	<title>Talk to Your Data</title>
	<meta name="description" content="Natural language interface for your data" />
</svelte:head>

<main>
	<div class="app-container">
		<aside class="sidebar">
			<div class="sidebar-header">
				<h1>Talk to Data</h1>
			</div>
			<div class="tabs">
				<button 
					class="tab-btn" 
					class:active={activeTab === 'chat'} 
					on:click={() => handleTabChange('chat')}
				>
					Chat
				</button>
				<button 
					class="tab-btn" 
					class:active={activeTab === 'analysis'} 
					on:click={() => handleTabChange('analysis')}
				>
					Analysis
				</button>
			</div>
			<div class="sidebar-content">
				<ChatHistory {chats} on:chatSelected={handleChatSelect} />
			</div>
		</aside>

		<div class="main-content">
			{#if activeTab === 'chat'}
				<div class="chat-container">
					<div class="chat-header">
						<h2>Chat with your data</h2>
					</div>
					<div class="chat-messages">
						{#if results.length > 0}
							<div class="message user">
								<div class="message-content">
									<p>Show me the data</p>
								</div>
							</div>
							<div class="message assistant">
								<div class="message-content">
									<QueryResults {results} {loading} {error} />
								</div>
							</div>
						{/if}
					</div>
					<div class="chat-input">
						<QueryInput on:querySubmitted={handleQuerySubmit} />
					</div>
				</div>
			{:else}
				<Analysis />
			{/if}
		</div>
	</div>

	<div class="container">
		<FileUpload on:uploadComplete={handleUploadComplete} />
	</div>
</main>

<style>
	:global(body) {
		margin: 0;
		background-color: #ffffff;
		color: #333333;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
	}

	.app-container {
		display: grid;
		grid-template-columns: 260px 1fr;
		height: 100vh;
	}

	.sidebar {
		background-color: #f9f9f9;
		border-right: 1px solid #e0e0e0;
		display: flex;
		flex-direction: column;
	}

	.sidebar-header {
		padding: 1rem;
		border-bottom: 1px solid #e0e0e0;
	}

	.sidebar-header h1 {
		margin: 0;
		font-size: 1.25rem;
		color: #333333;
	}

	.tabs {
		display: flex;
		padding: 1rem;
		gap: 0.5rem;
		border-bottom: 1px solid #e0e0e0;
	}

	.tab-btn {
		flex: 1;
		padding: 0.5rem;
		border: none;
		background: none;
		cursor: pointer;
		border-radius: 4px;
		font-size: 0.9rem;
		color: #666;
		transition: all 0.2s ease;
	}

	.tab-btn:hover {
		background-color: #f0f0f0;
	}

	.tab-btn.active {
		background-color: #e0e0e0;
		color: #333;
		font-weight: 500;
	}

	.sidebar-content {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
	}

	.main-content {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: #ffffff;
	}

	.chat-container {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.chat-header {
		padding: 1rem;
		border-bottom: 1px solid #e0e0e0;
		background-color: #ffffff;
	}

	.chat-header h2 {
		margin: 0;
		font-size: 1.25rem;
		color: #333333;
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		background-color: #ffffff;
	}

	.message {
		display: flex;
		padding: 1rem;
		margin-bottom: 1rem;
	}

	.message.user {
		background-color: #f0f0f0;
		border-radius: 0.5rem;
	}

	.message.assistant {
		background-color: #f0f0f0;
		border-radius: 0.5rem;
	}

	.message-content {
		max-width: 800px;
		margin: 0 auto;
		width: 100%;
	}

	.message-content p {
		margin: 0;
		color: #333333;
	}

	.chat-input {
		padding: 1rem;
		border-top: 1px solid #e0e0e0;
		background-color: #ffffff;
	}

	@media (max-width: 768px) {
		.app-container {
			grid-template-columns: 1fr;
		}

		.sidebar {
			display: none;
		}
	}
</style>
