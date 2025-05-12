<script lang="ts">
  interface Category {
    id: string;
    name: string;
    type: 'income' | 'expense';
    color: string;
  }

  let categories: Category[] = [
    {
      id: '1',
      name: 'Salary',
      type: 'income',
      color: '#10B981'
    },
    {
      id: '2',
      name: 'Food',
      type: 'expense',
      color: '#EF4444'
    },
    {
      id: '3',
      name: 'Transportation',
      type: 'expense',
      color: '#3B82F6'
    }
  ];

  let newCategory = {
    name: '',
    type: 'expense' as 'income' | 'expense',
    color: '#3B82F6'
  };

  function addCategory() {
    categories = [
      ...categories,
      {
        id: Date.now().toString(),
        ...newCategory
      }
    ];
    newCategory = {
      name: '',
      type: 'expense',
      color: '#3B82F6'
    };
  }

  function deleteCategory(id: string) {
    categories = categories.filter(category => category.id !== id);
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-semibold text-gray-900">Categories</h1>
    <button
      class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      on:click={() => document.getElementById('new-category-modal')?.classList.remove('hidden')}
    >
      Add Category
    </button>
  </div>

  <!-- New Category Modal -->
  <div id="new-category-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium text-gray-900">Add New Category</h3>
        <form on:submit|preventDefault={addCategory} class="mt-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Name</label>
            <input
              type="text"
              bind:value={newCategory.name}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Type</label>
            <select
              bind:value={newCategory.type}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Color</label>
            <input
              type="color"
              bind:value={newCategory.color}
              class="mt-1 block w-full h-10 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              on:click={() => document.getElementById('new-category-modal')?.classList.add('hidden')}
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

  <!-- Categories Grid -->
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
    {#each categories as category}
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div
                class="w-4 h-4 rounded-full mr-3"
                style="background-color: {category.color}"
              ></div>
              <h3 class="text-lg font-medium text-gray-900">{category.name}</h3>
            </div>
            <button
              class="text-gray-400 hover:text-gray-500"
              on:click={() => deleteCategory(category.id)}
            >
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
          <div class="mt-2">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {category.type === 'income' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
              {category.type}
            </span>
          </div>
        </div>
      </div>
    {/each}
  </div>
</div> 