import { createApp } from 'vue'
import DecisionTreeEditor from './components/DecisionTreeEditor.vue'

const mountEl = document.getElementById('DT-valutabile')

if (mountEl) {
    // 1. Estraiamo il JSON iniettato da Flask
    const rawData = mountEl.dataset.tree;
    const treeData = JSON.parse(rawData);
    const deviceId = mountEl.dataset.deviceId;

    // 2. Avviamo l'app passando i dati iniziali
    createApp(DecisionTreeEditor, { 
        initialTree: treeData,
        deviceId: deviceId
    }).mount('#DT-valutabile')
}