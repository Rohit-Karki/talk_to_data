<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';

  onMount(() => {
    goto('/dashboard');
  });
</script>

<div class="min-h-screen flex items-center justify-center">
  <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
</div>
