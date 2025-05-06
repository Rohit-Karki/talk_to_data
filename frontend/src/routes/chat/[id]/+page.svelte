<script lang="ts">
    import { page } from '$app/stores';
    import QueryInput from '$lib/components/QueryInput.svelte';
    import QueryResults from '$lib/components/QueryResults.svelte';

    let results: Array<Record<string, any>> = [];
    let loading = false;
    let error: string | null = null;
    let chatTitle = '';

    // In a real application, you would fetch the chat history based on the ID
    $: {
        const chatId = $page.params.id;
        // Here you would typically fetch the chat history from your backend
        chatTitle = `Chat ${chatId}`;
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
                body: JSON.stringify({ 
                    question: query,
                    chatId: $page.params.id 
                })
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
</script>

<div class="chat-container">
    <div class="chat-header">
        <h2>{chatTitle}</h2>
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

<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
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
</style> 