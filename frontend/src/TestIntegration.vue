<template>
  <div style="background-color: yellow; padding: 20px; border: 5px solid red; margin-top: 20px;">
    <h2 style="color: black;">🚀 VUE È VIVO E FUNZIONA!</h2>
    <p style="color: black;">Se vedi questo box, l'integrazione con Flask è perfetta.</p>
    <button @click="contatore++" style="padding: 10px; font-size: 16px;">
      Test Reattività: {{ contatore }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
const contatore = ref(0)
</script>