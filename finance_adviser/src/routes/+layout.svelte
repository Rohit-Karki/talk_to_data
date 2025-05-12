<script lang="ts">
	import '../app.css';
</script>

<div class="min-h-screen bg-gray-100">
	<nav class="bg-white shadow-lg">
		<div class="max-w-7xl mx-auto px-4">
			<div class="flex justify-between h-16">
				<div class="flex">
					<div class="flex-shrink-0 flex items-center">
						<h1 class="text-xl font-bold text-gray-800">Finance Advisor</h1>
					</div>
					<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
						<a href="/dashboard" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">Dashboard</a>
						<a href="/transactions" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">Transactions</a>
						<a href="/budget" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">Budget</a>
						<a href="/categories" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">Categories</a>
						<a href="/reports" class="text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 border-transparent hover:border-gray-300">Reports</a>
					</div>
				</div>
				<div class="flex items-center">
					<a href="/auth/login" class="text-gray-900 inline-flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100">Login</a>
				</div>
			</div>
		</div>
	</nav>

	<main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
		<slot />
	</main>
</div>
