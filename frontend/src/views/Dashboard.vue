<template>
  <div>
    <h2>Dashboard Dispositivo</h2>

    <div v-if="errore" style="color: red; padding: 1rem; border: 1px solid red;">
      {{ errore }}
    </div>

    <div v-else-if="caricamento">
      <p> Caricamento dati da MongoDB in corso...</p>
    </div>

    <div v-else-if="dashboardData" class="dashboard-container">

      <div style="background: #eef; padding: 1rem; border-radius: 8px; margin-bottom: 2rem;">
        <h3>{{ dashboardData.device.info.name }}</h3>
        <p><strong>OS:</strong> {{ dashboardData.device.info.os }}</p>
        <p><strong>Descrizione:</strong> {{ dashboardData.device.info.description }}</p>
        <p>
          <strong>Stato Globale:</strong>
          <span :style="{ color: dashboardData.device_status === 'Conforme' ? 'green' : 'orange' }">
            {{ dashboardData.device_status }}
          </span>
        </p>
      </div>

      <h3>Asset del dispositivo</h3>
      <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <thead style="background: #ddd;">
          <tr>
            <th>Nome Asset</th>
            <th>Tipo</th>
            <th>Stato</th>
            <th>Azioni</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(asset, index) in dashboardData.device.assets" :key="index">
            <td>{{ asset.name }}</td>
            <td>{{ asset.type }}</td>
            <td :style="{ color: asset.aggregated_status === 'Conforme' ? 'green' : 'orange' }">
              {{ asset.aggregated_status }}
            </td>
            <td>
              <router-link :to="`/editor/${route.params.id}/${index}/ACM-1`"
                style="background: #3498db; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px;">
                Valuta Asset
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top: 2rem; border-top: 1px solid #ccc; padding-top: 1rem;">
        <router-link :to="`/report/${route.params.id}`"
          style="background: #9b59b6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 1.1rem;">
          Visualizza Report Finale
        </router-link>
      </div>

    </div>

    <br>
    <router-link to="/">⬅ Torna all'Import</router-link>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const dashboardData = ref(null)
const caricamento = ref(true)
const errore = ref(null)

onMounted(async () => {
  try {
    // Chiamiamo la nuova API che abbiamo scritto in Flask
    const risposta = await fetch(`/api/dashboard/${route.params.id}`, {
      cache: 'no-store' // <- Costringe il browser a chiedere i dati freschi a Flask
    })

    // Se Flask restituisce 404 o 400, catturiamo l'errore
    if (!risposta.ok) {
      const datiErrore = await risposta.json()
      throw new Error(datiErrore.error || "Errore sconosciuto dal server")
    }

    // Salviamo i dati reali di MongoDB nella variabile reattiva
    dashboardData.value = await risposta.json()
  } catch (err) {
    errore.value = err.message
  } finally {
    caricamento.value = false
  }
})

// Funzione placeholder per i pulsanti della tabella
const apriAlbero = (indexAsset) => {
  alert(`In futuro, questo aprirà l'albero per l'asset numero ${indexAsset + 1}`)
}
</script>