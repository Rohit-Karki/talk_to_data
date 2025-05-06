<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import FileUpload from './FileUpload.svelte';
    
    let selectedFile: string | null = null;
    let analysisQuery = '';
    let loading = false;
    let error: string | null = null;
    let chartData: string | null = null; // Base64 encoded image data

    async function handleFileUpload(event: CustomEvent<{ filename: string }>) {
        selectedFile = event.detail.filename;
    }

    async function handleAnalysisSubmit() {
        if (!selectedFile || !analysisQuery) {
            error = 'Please select a file and enter your analysis query';
            return;
        }

        loading = true;
        error = null;
        chartData = null;

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
            chartData = data.chart_data; // Base64 encoded image
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to generate analysis';
        } finally {
            loading = false;
        }
    }
</script>

<div class="analysis-container">
    <div class="analysis-header">
        <h2>Data Analysis</h2>
    </div>

    <div class="analysis-content">
        <div class="file-section">
            <h3>Upload Data File</h3>
            <FileUpload on:uploadComplete={handleFileUpload} />
            {#if selectedFile}
                <div class="selected-file">
                    Selected file: {selectedFile}
                </div>
            {/if}
        </div>

        <div class="query-section">
            <h3>Analysis Query</h3>
            <div class="query-input">
                <textarea
                    bind:value={analysisQuery}
                    placeholder="Enter your analysis query (e.g., 'Create a bar chart of sales by region')"
                    rows="4"
                ></textarea>
                <button
                    on:click={handleAnalysisSubmit}
                    disabled={!selectedFile || !analysisQuery || loading}
                    class="submit-button"
                >
                    {loading ? 'Generating...' : 'Generate Analysis'}
                </button>
            </div>
        </div>

        {#if error}
            <div class="error-message">{error}</div>
        {/if}

        {#if chartData}
            <div class="chart-section">
                <h3>Analysis Results</h3>
                <div class="chart-container">
                    <img src={`data:image/png;base64,${chartData}`} alt="Analysis Chart" />
                </div>
            </div>
        {/if}
    </div>
</div>

<style>
    .analysis-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        background-color: #ffffff;
    }

    .analysis-header {
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
    }

    .analysis-header h2 {
        margin: 0;
        font-size: 1.25rem;
        color: #333333;
    }

    .analysis-content {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }

    .file-section,
    .query-section,
    .chart-section {
        margin-bottom: 2rem;
    }

    h3 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        color: #333333;
    }

    .selected-file {
        margin-top: 0.5rem;
        padding: 0.5rem;
        background-color: #f0f0f0;
        border-radius: 4px;
        font-size: 0.9rem;
    }

    .query-input {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    textarea {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
        font-size: 0.9rem;
        resize: vertical;
    }

    .submit-button {
        padding: 0.75rem 1.5rem;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9rem;
        align-self: flex-start;
    }

    .submit-button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .error-message {
        color: #ff0000;
        margin: 1rem 0;
        padding: 0.5rem;
        background-color: #fff0f0;
        border-radius: 4px;
    }

    .chart-container {
        margin-top: 1rem;
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 4px;
        text-align: center;
    }

    .chart-container img {
        max-width: 100%;
        height: auto;
    }
</style> 