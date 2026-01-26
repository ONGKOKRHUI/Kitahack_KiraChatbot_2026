<!-- ➡️ Contains the chat UI
➡️ Imports <Sidebar>
➡️ Sends messages to the backend -->

<script setup>
import { ref } from 'vue';
import Sidebar from '../components/Sidebar.vue';
import axios from 'axios';
import { PaperAirplaneIcon } from '@heroicons/vue/24/solid';

const currentSessionId = ref(null);
const messages = ref([]);
const userInput = ref('');
const loading = ref(false);

// Fetch messages when user clicks a session in Sidebar
const loadMessages = async (sessionId) => {
  currentSessionId.value = sessionId;
  try {
    const res = await axios.get(`http://localhost:8000/api/v1/chat/sessions/${sessionId}/messages`);
    messages.value = res.data;
  } catch (e) {
    console.error("Error loading messages:", e);
  }
};

const sendMessage = async () => {
  if (!userInput.value.trim() || !currentSessionId.value) return;

  const text = userInput.value;
  userInput.value = '';
  
  // 1. Optimistic UI: Show user message immediately
  messages.value.push({ role: 'user', content: text });
  loading.value = true;

  try {
    // 2. Call Python Backend
    // when user presses enter or clicks send (sendMessage)
    // sends a POST request to http://localhost:8000/api/v1/chat/send
    // with session_id and user_query
    const res = await axios.post('http://localhost:8000/api/v1/chat/send', {
      session_id: currentSessionId.value,
      user_query: text
    });
    
    // 3. Update UI with AI response received (returned) from backend
    messages.value.push(res.data);
  } catch (e) {
    messages.value.push({ role: 'assistant', content: "⚠️ Error: Could not connect to Cockpit." });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <Sidebar :currentSessionId="currentSessionId" @select-session="loadMessages" />

    <div class="flex flex-col flex-1 h-full">
      
      <div class="flex-1 p-8 overflow-y-auto scroll-smooth">
        <div v-if="!currentSessionId" class="flex flex-col items-center justify-center h-full text-gray-400">
          <p class="text-xl font-medium">Select a project to start chatting</p>
        </div>

        <div v-else v-for="(msg, index) in messages" :key="index" class="mb-6">
          <div :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">
            <div :class="['max-w-2xl px-5 py-3 rounded-2xl text-sm leading-6 shadow-sm', 
                          msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white border text-gray-800 rounded-bl-none']">
              <p class="whitespace-pre-wrap font-sans">{{ msg.content }}</p>
            </div>
          </div>
        </div>
        
        <div v-if="loading" class="flex justify-start mb-6">
           <div class="px-5 py-3 text-sm text-gray-500 bg-white border rounded-2xl animate-pulse">
             Retrieving knowledge...
           </div>
        </div>
      </div>

      <div class="p-6 bg-white border-t border-gray-200">
        <div class="flex max-w-4xl mx-auto space-x-4">
          <input 
            v-model="userInput" 
            @keyup.enter="sendMessage"
            type="text" 
            placeholder="Ask about project decisions, actions, or summaries..." 
            class="flex-1 p-4 text-gray-700 bg-gray-100 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            :disabled="!currentSessionId || loading"
          />
          <button 
            @click="sendMessage" 
            :disabled="!currentSessionId || loading"
            class="p-4 text-white transition-colors bg-blue-600 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
            <PaperAirplaneIcon class="w-6 h-6 transform -rotate-45" />
          </button>
        </div>
      </div>

    </div>
  </div>
</template>