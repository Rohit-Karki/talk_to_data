<script lang="ts">
    let question = '';
    let answer: string | null = null;
    let loading = false;
    let error: string | null = null;
    let filename = 'bank.csv'; // Default SMS CSV file

    async function handleSubmit() {
        if (!question) {
            error = 'Please enter a question.';
            return;
        }
        loading = true;
        error = null;
        answer = null;
        try {
            const response = await fetch('http://localhost:5000/api/rag-query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename, question })
            });
            if (!response.ok) {
                throw new Error('Failed to get answer from backend');
            }
            const data = await response.json();
            answer = data.answer || data.result || JSON.stringify(data);
        } catch (e) {
            error = e instanceof Error ? e.message : 'Unknown error';
        } finally {
            loading = false;
        }
    }
</script>

<div class="rag-query-container">
    <h2>RAG Query: Financial SMS Data</h2>
    <form on:submit|preventDefault={handleSubmit}>
        <label for="question">Ask a question about the SMS data:</label>
        <textarea id="question" bind:value={question} rows="3" placeholder="e.g. What is the highest deposit amount?"></textarea>
        <button type="submit" disabled={loading}>{loading ? 'Querying...' : 'Ask'}</button>
    </form>
    {#if error}
        <div class="error">{error}</div>
    {/if}
    {#if answer}
        <div class="answer">
            <h3>Answer:</h3>
            <pre>{answer}</pre>
        </div>
    {/if}
</div>

<style>
.rag-query-container {
    max-width: 600px;
    margin: 2rem auto;
    padding: 2rem;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
label {
    font-weight: bold;
    display: block;
    margin-bottom: 0.5rem;
}
textarea {
    width: 100%;
    margin-bottom: 1rem;
    padding: 0.5rem;
    border-radius: 4px;
    border: 1px solid #ccc;
    font-size: 1rem;
}
button {
    padding: 0.5rem 1.5rem;
    border: none;
    border-radius: 4px;
    background: #0070f3;
    color: #fff;
    font-size: 1rem;
    cursor: pointer;
}
button[disabled] {
    background: #aaa;
    cursor: not-allowed;
}
.error {
    color: #c00;
    margin-top: 1rem;
}
.answer {
    margin-top: 2rem;
    background: #f7f7fa;
    padding: 1rem;
    border-radius: 6px;
}
pre {
    white-space: pre-wrap;
    word-break: break-word;
}
</style> 