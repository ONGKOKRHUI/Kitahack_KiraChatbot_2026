<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // We'll use the store we set up

const router = useRouter();
const authStore = useAuthStore();
const projects = ref(authStore.user?.projects || [])

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  errorMessage.value = '';
  isLoading.value = true;

  try {
    // 1. Call the Login Action from our Store
    // This abstracts the logic (e.g., saving the token) away from the view
    const success = await authStore.login(username.value, password.value);

    if (success) {
      // 2. Redirect to the Chat Page (Home)
      router.push('/'); 
    } else {
      errorMessage.value = 'Invalid credentials';
    }
  } catch (error) {
    errorMessage.value = 'Login failed. Please check your connection.';
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100">
    <div class="w-full max-w-md p-8 bg-white rounded-lg shadow-md">
      
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-800">Welcome Back</h1>
        <p class="text-sm text-gray-500">Sign in to access the Knowledge Base</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-6">
        
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
          <div class="mt-1">
            <input 
              id="username" 
              v-model="username" 
              type="text" 
              required 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your username"
            />
          </div>
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <div class="mt-1">
            <input 
              id="password" 
              v-model="password" 
              type="password" 
              required 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="••••••••"
            />
          </div>
        </div>

        <div v-if="errorMessage" class="text-sm text-red-600 bg-red-50 p-2 rounded">
          {{ errorMessage }}
        </div>

        <div>
          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isLoading ? 'Signing in...' : 'Sign in' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>