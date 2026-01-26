<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { PlusIcon, ChatBubbleLeftIcon } from '@heroicons/vue/24/outline';

// Props: Data passed down from the parent (HomeView)
const props = defineProps(['currentSessionId']);

// Emits: Events we send UP to the parent
const emit = defineEmits(['select-session']);

// Data State
const projects = ref([]);          // Replaces mock data
const selectedProject = ref('');
const sessions = ref([]);
const loading = ref(true);

// API Configuration
const API_URL = 'http://localhost:8000/api/v1';

// 1. Fetch Projects & Sessions on Load
onMounted(async () => {
  try {
    // A. Fetch available projects (You might need to add a small API endpoint for this or hardcode for now)
    // For now, let's assume we fetch them or just define them if they are static
    projects.value = ['A100 - Chatbot', 'B200 - Analytics']; 
    selectedProject.value = projects.value[0];

    // B. Fetch Chat History from Backend
    await fetchSessions();
  } catch (e) {
    console.error("Backend connection failed:", e);
  } finally {
    loading.value = false;
  }
});

// Function to get history from backend
const fetchSessions = async () => {
  try {
    // CALLING YOUR PYTHON BACKEND HERE
    const res = await axios.get(`${API_URL}/chat/sessions`);
    sessions.value = res.data;
  } catch (e) {
    console.error("Failed to load sessions");
  }
};

const createNewChat = async () => {
  try {
    // Parse the project code (e.g., "A100" from "A100 - Chatbot")
    const projectCode = selectedProject.value.split(' ')[0];

    // CALLING BACKEND TO CREATE SESSION
    const res = await axios.post(`${API_URL}/chat/sessions`, {
      project_code: projectCode,
      title: "New Conversation"
    });
    
    // Refresh list and select the new one
    await fetchSessions();
    emit('select-session', res.data.session_id);
  } catch (e) {
    console.error(e);
  }
};
</script>

<template>
  <div class="flex flex-col h-full text-gray-300 bg-gray-900 w-72 border-r border-gray-800">
    
    <div class="p-4">
      <h2 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Project</h2>
      <select v-model="selectedProject" class="w-full bg-gray-800 text-white rounded p-2 border border-gray-700 focus:outline-none focus:border-blue-500">
        <option v-for="p in projects" :key="p">{{ p }}</option>
      </select>

      <button @click="createNewChat" class="w-full mt-4 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded transition-colors">
        <PlusIcon class="w-5 h-5" />
        <span>New Chat</span>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-2">
      <div v-if="loading" class="text-center text-gray-500 mt-4">Loading...</div>
      
      <div v-else>
        <div class="px-2 mb-2 text-xs font-semibold text-gray-500 uppercase">History</div>
        
        <div v-for="session in sessions" :key="session.id" 
             @click="$emit('select-session', session.id)"
             :class="['flex items-center px-3 py-3 rounded cursor-pointer mb-1 transition-colors', 
                      session.id === currentSessionId ? 'bg-gray-800 text-white shadow-sm' : 'hover:bg-gray-800 text-gray-400']">
          <ChatBubbleLeftIcon class="w-4 h-4 mr-3 flex-shrink-0" />
          <span class="text-sm truncate">{{ session.title }}</span>
        </div>
      </div>
    </div>
  </div>
</template>