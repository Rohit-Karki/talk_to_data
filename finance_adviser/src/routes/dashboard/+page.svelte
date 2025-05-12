<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let balance = 0;
  let income = 0;
  let expenses = 0;
  let chartCanvas: HTMLCanvasElement;

  onMount(() => {
    // Initialize chart
    const ctx = chartCanvas.getContext('2d');
    if (ctx) {
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [{
            label: 'Balance',
            data: [1200, 1900, 1500, 2100, 1800, 2400],
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
          }]
        }
      });
    }
  });
</script>

<div class="space-y-6">
  <h1 class="text-2xl font-semibold text-gray-900">Dashboard</h1>
  
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
    <!-- Balance Card -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Total Balance</dt>
              <dd class="text-lg font-medium text-gray-900">${balance}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- Income Card -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Monthly Income</dt>
              <dd class="text-lg font-medium text-gray-900">${income}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- Expenses Card -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Monthly Expenses</dt>
              <dd class="text-lg font-medium text-gray-900">${expenses}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Chart -->
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-lg font-medium text-gray-900 mb-4">Balance History</h2>
    <canvas bind:this={chartCanvas}></canvas>
  </div>
</div> 