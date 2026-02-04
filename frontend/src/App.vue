<!-- ➡️ The root layout
➡️ Contains <router-view />, which loads the current page -->

<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* use Tailwind mostly */
html, body, #app {
  height: 100%;
  margin: 0;
}
</style>
