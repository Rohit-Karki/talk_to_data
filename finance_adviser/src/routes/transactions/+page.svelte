<script lang="ts">
  import { format } from 'date-fns';

  interface Transaction {
    id: string;
    date: Date;
    description: string;
    amount: number;
    category: string;
    type: 'income' | 'expense';
  }

  let transactions: Transaction[] = [
    {
      id: '1',
      date: new Date('2024-03-10'),
      description: 'Salary',
      amount: 5000,
      category: 'Income',
      type: 'income'
    },
    {
      id: '2',
      date: new Date('2024-03-09'),
      description: 'Grocery Shopping',
      amount: 150,
      category: 'Food',
      type: 'expense'
    }
  ];

  let newTransaction = {
    description: '',
    amount: 0,
    category: '',
    type: 'expense' as 'income' | 'expense'
  };

  function addTransaction() {
    transactions = [
      {
        id: Date.now().toString(),
        date: new Date(),
        ...newTransaction
      },
      ...transactions
    ];
    newTransaction = {
      description: '',
      amount: 0,
      category: '',
      type: 'expense'
    };
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-semibold text-gray-900">Transactions</h1>
    <button
      class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
      on:click={() => document.getElementById('new-transaction-modal')?.classList.remove('hidden')}
    >
      Add Transaction
    </button>
  </div>

  <!-- New Transaction Modal -->
  <div id="new-transaction-modal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
    <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3">
        <h3 class="text-lg font-medium text-gray-900">Add New Transaction</h3>
        <form on:submit|preventDefault={addTransaction} class="mt-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Description</label>
            <input
              type="text"
              bind:value={newTransaction.description}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Amount</label>
            <input
              type="number"
              bind:value={newTransaction.amount}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Category</label>
            <input
              type="text"
              bind:value={newTransaction.category}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Type</label>
            <select
              bind:value={newTransaction.type}
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="income">Income</option>
              <option value="expense">Expense</option>
            </select>
          </div>
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              on:click={() => document.getElementById('new-transaction-modal')?.classList.add('hidden')}
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

  <!-- Transactions Table -->
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        {#each transactions as transaction}
          <tr>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {format(transaction.date, 'MMM d, yyyy')}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{transaction.description}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{transaction.category}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm {transaction.type === 'income' ? 'text-green-600' : 'text-red-600'}">
              {transaction.type === 'income' ? '+' : '-'}${Math.abs(transaction.amount)}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div> 