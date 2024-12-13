<template>
  <div id="app">
    <h1>Jogo da Vida (IA)</h1>
    <GameGrid />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import GameGrid from './components/GameGrid.vue'

export default defineComponent({
  name: 'App',
  components: {
    GameGrid
  }
})
</script>

<style>
</style>
