<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let chats: Array<{
    id: string;
    title: string;
    timestamp: string;
    preview: string;
  }> = [];
  
  const dispatch = createEventDispatcher();
  
  function handleChatClick(chat: { id: string; title: string; timestamp: string; preview: string }) {
    dispatch('chatSelected', { chat });
  }
</script>

<div class="chat-history">
  <h3>Chat History</h3>
  {#if chats.length === 0}
    <p class="empty-state">No chat history yet</p>
  {:else}
    <div class="chats">
      {#each chats as chat}
        <button class="chat-item" on:click={() => handleChatClick(chat)}>
          <div class="chat-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="chat-info">
            <span class="chat-title">{chat.title}</span>
            <span class="chat-preview">{chat.preview}</span>
            <span class="chat-timestamp">{chat.timestamp}</span>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .chat-history {
    margin-top: 1rem;
  }
  
  h3 {
    margin: 0 0 0.75rem 0;
    color: #666666;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .empty-state {
    color: #666666;
    text-align: center;
    padding: 1rem;
    font-size: 0.875rem;
  }
  
  .chats {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .chat-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background 0.2s ease;
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
    color: #333333;
  }
  
  .chat-item:hover {
    background-color: #f0f0f0;
  }
  
  .chat-icon {
    color: #666666;
    flex-shrink: 0;
    margin-top: 0.125rem;
  }
  
  .chat-info {
    display: flex;
    flex-direction: column;
    min-width: 0;
    gap: 0.25rem;
  }
  
  .chat-title {
    font-size: 0.875rem;
    color: #333333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .chat-preview {
    font-size: 0.75rem;
    color: #666666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .chat-timestamp {
    font-size: 0.75rem;
    color: #666666;
  }
</style> 