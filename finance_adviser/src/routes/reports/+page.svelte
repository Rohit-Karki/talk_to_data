<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  let expenseChartCanvas: HTMLCanvasElement;
  let incomeChartCanvas: HTMLCanvasElement;
  let trendChartCanvas: HTMLCanvasElement;

  onMount(() => {
    // Expense Distribution Chart
    const expenseCtx = expenseChartCanvas.getContext('2d');
    if (expenseCtx) {
      new Chart(expenseCtx, {
        type: 'doughnut',
        data: {
          labels: ['Food', 'Transportation', 'Entertainment', 'Bills', 'Shopping'],
          datasets: [{
            data: [30, 20, 15, 25, 10],
            backgroundColor: [
              '#EF4444',
              '#3B82F6',
              '#10B981',
              '#F59E0B',
              '#8B5CF6'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Expense Distribution'
            }
          }
        }
      });
    }

    // Income Sources Chart
    const incomeCtx = incomeChartCanvas.getContext('2d');
    if (incomeCtx) {
      new Chart(incomeCtx, {
        type: 'pie',
        data: {
          labels: ['Salary', 'Freelance', 'Investments', 'Other'],
          datasets: [{
            data: [70, 15, 10, 5],
            backgroundColor: [
              '#10B981',
              '#3B82F6',
              '#F59E0B',
              '#6B7280'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Income Sources'
            }
          }
        }
      });
    }

    // Monthly Trend Chart
    const trendCtx = trendChartCanvas.getContext('2d');
    if (trendCtx) {
      new Chart(trendCtx, {
        type: 'line',
        data: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          datasets: [
            {
              label: 'Income',
              data: [5000, 5500, 5200, 5800, 5400, 6000],
              borderColor: '#10B981',
              tension: 0.1
            },
            {
              label: 'Expenses',
              data: [4000, 4200, 3800, 4500, 4100, 4300],
              borderColor: '#EF4444',
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: 'Monthly Income vs Expenses'
            }
          }
        }
      });
    }
  });
</script>

<div class="space-y-6">
  <h1 class="text-2xl font-semibold text-gray-900">Reports & Analytics</h1>

  <div class="grid grid-cols-1 gap-5 lg:grid-cols-2">
    <!-- Expense Distribution -->
    <div class="bg-white shadow rounded-lg p-6">
      <canvas bind:this={expenseChartCanvas}></canvas>
    </div>

    <!-- Income Sources -->
    <div class="bg-white shadow rounded-lg p-6">
      <canvas bind:this={incomeChartCanvas}></canvas>
    </div>

    <!-- Monthly Trend -->
    <div class="bg-white shadow rounded-lg p-6 lg:col-span-2">
      <canvas bind:this={trendChartCanvas}></canvas>
    </div>
  </div>

  <!-- Summary Cards -->
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
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
              <dt class="text-sm font-medium text-gray-500 truncate">Total Income</dt>
              <dd class="text-lg font-medium text-gray-900">$32,900</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

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
              <dt class="text-sm font-medium text-gray-500 truncate">Total Expenses</dt>
              <dd class="text-lg font-medium text-gray-900">$24,900</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Net Savings</dt>
              <dd class="text-lg font-medium text-gray-900">$8,000</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="p-5">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">Savings Rate</dt>
              <dd class="text-lg font-medium text-gray-900">24.3%</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  </div>
</div> 