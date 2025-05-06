<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  export let files: Array<{ name: string; preview: string }> = [];
  const dispatch = createEventDispatcher();
  
  function handleFileClick(file: { name: string; preview: string }) {
    dispatch('fileSelected', { file });
  }
</script>

<div class="file-list">
  <h3>Uploaded Files</h3>
  {#if files.length === 0}
    <p class="empty-state">No files uploaded yet</p>
  {:else}
    <div class="files">
      {#each files as file}
        <button class="file-item" on:click={() => handleFileClick(file)}>
          <div class="file-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">{file.name}</span>
            <span class="file-preview">{file.preview}</span>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .file-list {
    margin-top: 1rem;
  }
  
  h3 {
    margin: 0 0 0.75rem 0;
    color: #8e8ea0;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .empty-state {
    color: #8e8ea0;
    text-align: center;
    padding: 1rem;
    font-size: 0.875rem;
  }
  
  .files {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .file-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 0.75rem;
    border-radius: 0.375rem;
    cursor: pointer;
    transition: background 0.2s ease;
    background: transparent;
    border: none;
    width: 100%;
    text-align: left;
    color: #fff;
  }
  
  .file-item:hover {
    background-color: #2a2b32;
  }
  
  .file-icon {
    color: #8e8ea0;
    flex-shrink: 0;
  }
  
  .file-info {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  
  .file-name {
    font-size: 0.875rem;
    color: #fff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .file-preview {
    font-size: 0.75rem;
    color: #8e8ea0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
</style> 