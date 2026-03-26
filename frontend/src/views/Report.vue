<template>
  <div style="max-width: 1000px; margin: 0 auto; padding-bottom: 5rem;">
    <h2>Report Dispositivo</h2>

    <div v-if="caricamento">⏳ Caricamento report...</div>
    <div v-else-if="errore" style="color: red;">{{ errore }}</div>

    <div v-else-if="reportData">
      <div style="background: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem;">
        <h3>{{ reportData.device_info.name }}</h3>
        <p><strong>OS:</strong> {{ reportData.device_info.os }}</p>
        
        <div v-if="!reportData.all_assessed" style="background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px; margin-top: 10px;">
          ⚠️ <strong>Attenzione:</strong> Non tutti i requisiti sono stati valutati. Il report è parziale.
        </div>
      </div>

      <div v-for="asset in reportData.assets" :key="asset.name" style="margin-bottom: 3rem; background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        
        <div style="margin-bottom: 1rem;">
          <span style="background: #3b7dee; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">
            {{ asset.type.toUpperCase() }}
          </span>
          <h3 style="margin: 0.5rem 0 0.2rem 0; color: #1a1a2e;">{{ asset.name }}</h3>
          <p style="color: #666; font-size: 0.9rem; margin: 0;">{{ asset.description }}</p>
        </div>

        <table border="1" style="width: 100%; border-collapse: collapse; text-align: center; border-color: #dde1e7;">
          <thead style="background: #2c3e50; color: white;">
            <tr>
              <th style="padding: 8px;">DN / ACM</th>
              <th v-for="col in reportData.columns" :key="col" style="padding: 8px;">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in reportData.rows" :key="row">
              <td style="font-weight: bold; background: #f0f2f5; padding: 8px; text-align: left;">
                {{ row }}
              </td>
              <td v-for="col in reportData.columns" :key="col" 
                  :style="stileCella(ottieniValore(asset, col, row))"
                  style="padding: 8px;">
                {{ testoValore(ottieniValore(asset, col, row)) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div style="display: flex; gap: 15px;">
        <router-link :to="`/dashboard/${route.params.id}`" 
           style="padding: 10px 20px; background: #95a5a6; color: white; text-decoration: none; border-radius: 4px;">
           ⬅ Torna alla Dashboard
        </router-link>

        <a :href="`/api/report/${route.params.id}/export`" target="_blank"
           style="padding: 10px 20px; background: #e74c3c; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">
           📄 Scarica PDF
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const reportData = ref(null)
const caricamento = ref(true)
const errore = ref(null)

onMounted(async () => {
  try {
    const res = await fetch(`/api/report/${route.params.id}`, { cache: 'no-store' })
    if (!res.ok) throw new Error("Errore nel caricamento del report")
    reportData.value = await res.json()
  } catch (err) {
    errore.value = err.message
  } finally {
    caricamento.value = false
  }
})

// Estrae il valore safely dal dizionario python convertito in JSON
const ottieniValore = (asset, colonna, riga) => {
  if (asset.dt && asset.dt[colonna] && asset.dt[colonna][riga] !== undefined) {
    return asset.dt[colonna][riga]
  }
  return null
}

// Replica i colori esatti del tuo FPDF in Python
const stileCella = (valore) => {
  if (valore === true) return "background: #e6f9ec; color: #1e7e34; font-weight: bold;"
  if (valore === false) return "background: #fdecea; color: #c0392b; font-weight: bold;"
  return "background: #f0f0f0; color: #888888;" // N.A.
}

const testoValore = (valore) => {
  if (valore === true) return "True"
  if (valore === false) return "False"
  return "N.A."
}
</script>