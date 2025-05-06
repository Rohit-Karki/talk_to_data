<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  let query = '';
  
  function handleSubmit() {
    if (query.trim()) {
      dispatch('querySubmitted', { query: query.trim() });
      query = '';
    }
  }
  
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="query-input">
  <div class="input-container">
    <textarea
      bind:value={query}
      on:keydown={handleKeydown}
      placeholder="Message Talk to Data..."
      rows="1"
    ></textarea>
    <button 
      class="send-button" 
      on:click={handleSubmit} 
      disabled={!query.trim()}
      title="Send message"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 2L11 13"/>
        <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
      </svg>
    </button>
  </div>
  <div class="input-footer">
    <span class="hint">Press Enter to send, Shift + Enter for new line</span>
  </div>
</div>

<style>
  .query-input {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 0.5rem;
    padding: 0.75rem;
  }
  
  .input-container {
    display: flex;
    gap: 0.5rem;
    align-items: flex-end;
  }
  
  textarea {
    flex: 1;
    border: 1px solid #e0e0e0;
    border-radius: 0.375rem;
    padding: 0.75rem;
    font-size: 0.875rem;
    line-height: 1.5;
    resize: none;
    background-color: #ffffff;
    color: #333333;
    min-height: 24px;
    max-height: 200px;
  }
  
  textarea:focus {
    outline: none;
    border-color: #666666;
  }
  
  textarea::placeholder {
    color: #666666;
  }
  
  .send-button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border: none;
    border-radius: 0.375rem;
    background-color: #f0f0f0;
    color: #666666;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .send-button:hover:not(:disabled) {
    background-color: #e0e0e0;
    color: #333333;
  }
  
  .send-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .input-footer {
    margin-top: 0.5rem;
  }
  
  .hint {
    font-size: 0.75rem;
    color: #666666;
  }
</style> 