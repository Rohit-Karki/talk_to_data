<script lang="ts">
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';

  async function handleSubmit() {
    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    try {
      // Here you would typically make an API call to your registration endpoint
      console.log('Registration attempt:', { email, password });
      // For now, we'll just redirect to the login page
      window.location.href = '/auth/login';
    } catch (e) {
      error = 'Registration failed. Please try again.';
    }
  }
</script>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-md w-full space-y-8">
    <div>
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Create your account
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        Or
        <a href="/auth/login" class="font-medium text-blue-600 hover:text-blue-500">
          sign in to your existing account
        </a>
      </p>
    </div>
    <form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
      <div class="rounded-md shadow-sm -space-y-px">
        <div>
          <label for="email-address" class="sr-only">Email address</label>
          <input
            id="email-address"
            name="email"
            type="email"
            autocomplete="email"
            required
            bind:value={email}
            class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="Email address"
          />
        </div>
        <div>
          <label for="password" class="sr-only">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            autocomplete="new-password"
            required
            bind:value={password}
            class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="Password"
          />
        </div>
        <div>
          <label for="confirm-password" class="sr-only">Confirm Password</label>
          <input
            id="confirm-password"
            name="confirm-password"
            type="password"
            autocomplete="new-password"
            required
            bind:value={confirmPassword}
            class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="Confirm Password"
          />
        </div>
      </div>

      {#if error}
        <div class="text-red-500 text-sm text-center">{error}</div>
      {/if}

      <div>
        <button
          type="submit"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Create Account
        </button>
      </div>
    </form>
  </div>
</div> 