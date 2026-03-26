<template>
  <div style="max-width: 500px; margin: 2rem auto; text-align: center;">
    <h2>Carica Configurazione Dispositivo</h2>
    
    <div style="border: 2px dashed #ccc; padding: 2rem; border-radius: 12px; background: white;">
      <input type="file" @change="selezionaFile" accept=".json" id="fileInput" hidden />
      <label for="fileInput" style="cursor: pointer; color: #3498db; font-weight: bold;">
        {{ file ? file.name : 'Clicca per selezionare un file JSON' }}
      </label>
      
      <div v-if="file" style="margin-top: 1rem;">
        <button @click="inviaAlServer" :disabled="caricando" 
                style="background: #2ecc71; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 5px; cursor: pointer;">
          {{ caricando ? 'Invio in corso...' : 'Conferma Importazione' }}
        </button>
      </div>
    </div>

    <p v-if="messaggioErrore" style="color: red; margin-top: 1rem;">{{ messaggioErrore }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const file = ref(null)
const caricando = ref(false)
const messaggioErrore = ref('')

const selezionaFile = (event) => {
  file.value = event.target.files[0]
  messaggioErrore.value = ''
}

const inviaAlServer = async () => {
  if (!file.value) return

  caricando.value = true
  const formData = new FormData()
  formData.append('file', file.value)

  try {
    const risposta = await fetch('/api/import', {
      method: 'POST',
      body: formData
    })

    const dati = await risposta.json()

    if (risposta.ok) {
      // NAVIGAZIONE SPA: Flask ha risposto OK, Vue cambia "pagina" senza ricaricare
      router.push(`/dashboard/${dati.device_id}`)
    } else {
      messaggioErrore.value = dati.error || 'Errore durante l\'importazione'
    }
  } catch (e) {
    messaggioErrore.value = 'Impossibile connettersi al server.'
  } finally {
    caricando.value = false
  }
}
</script>