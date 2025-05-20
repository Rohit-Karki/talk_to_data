<script lang="ts">
    import { page } from '$app/stores';
    import Analysis from '$lib/components/Analysis.svelte';
    
    // Get the thread ID from the URL params
    $: threadId = $page.params.id;
</script>

<Analysis initialThreadId={threadId} />