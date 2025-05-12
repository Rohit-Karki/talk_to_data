<script lang="ts">
  interface Budget {
    id: string;
    category: string;
    amount: number;
    spent: number;
  }

  let budgets: Budget[] = [
    {
      id: '1',
      category: 'Food',
      amount: 500,
      spent: 350
    },
    {
      id: '2',
      category: 'Transportation',
      amount: 200,
      spent: 150
    },
    {
      id: '3',
      category: 'Entertainment',
      amount: 300,
      spent: 200
    }
  ];

  let newBudget = {
    category: '',
    amount: 0
  };

  function addBudget() {
    budgets = [
      ...budgets,
      {
        id: Date.now().toString(),
        ...newBudget,
        spent: 0
      }
    ];
    newBudget = {
      category: '',
      amount: 0
    };
  }

  function getProgressColor(spent: number, amount: number) {
    const percentage = (spent / amount) * 100;
    if (percentage >= 90) return 'bg-red-600';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-semibold text-gray-900">Budget</h1>
    <button
      class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      on:click={() => document.getElementById('new-budget-modal')?.classList.remove('hidden')}
    >
      Add Budget
    </button>
  </div>

  <!-- New Budget Modal -->
  <div id="new-budget-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium text-gray-900">Add New Budget</h3>
        <form on:submit|preventDefault={addBudget} class="mt-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Category</label>
            <input
              type="text"
              bind:value={newBudget.category}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Amount</label>
            <input
              type="number"
              bind:value={newBudget.amount}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              on:click={() => document.getElementById('new-budget-modal')?.classList.add('hidden')}
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-500 hover:bg-blue-600 rounded-md"
            >
              Add
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Budget Cards -->
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
    {#each budgets as budget}
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900">{budget.category}</h3>
            <span class="text-sm text-gray-500">
              ${budget.spent} / ${budget.amount}
            </span>
          </div>
          <div class="mt-4">
            <div class="relative pt-1">
              <div class="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style="width: {(budget.spent / budget.amount) * 100}%"
                  class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center {getProgressColor(budget.spent, budget.amount)}"
                ></div>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <span class="text-sm text-gray-500">
              {Math.round((budget.spent / budget.amount) * 100)}% spent
            </span>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div> 