<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  let file: File | null = null;
  let uploading = false;
  let error: string | null = null;
  let success = false;
  
  async function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      file = input.files[0];
    }
  }
  
  async function uploadFile() {
    if (!file) return;

    uploading = true;
    error = null;
    success = false;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      success = true;
      dispatch('uploadComplete', { filename: data.filename });
    } catch (e) {
      error = e instanceof Error ? e.message : 'Upload failed';
    } finally {
      uploading = false;
    }
  }
</script>

<div class="file-upload">
  <div class="upload-container">
    <input
      type="file"
      on:change={handleFileSelect}
      accept="*/*"
      disabled={uploading}
    />
    <button
      on:click={uploadFile}
      disabled={!file || uploading}
      class="upload-button"
    >
      {uploading ? 'Uploading...' : 'Upload'}
    </button>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if success}
    <div class="success">File uploaded successfully!</div>
  {/if}
</div>

<style>
  .file-upload {
    margin: 1rem 0;
  }
  
  .upload-container {
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  
  .upload-button {
    padding: 0.5rem 1rem;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .upload-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .error {
    color: #ff0000;
    margin-top: 0.5rem;
  }
  
  .success {
    color: #4CAF50;
    margin-top: 0.5rem;
  }
</style> 