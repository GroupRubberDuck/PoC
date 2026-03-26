<template>
  <div id="tree-container" style="width: 100%; height: 600px; overflow: auto; background: #f8f9fa; border-radius: 8px;">
    <svg width="100%" height="100%" :viewBox="`0 0 ${svgWidth} ${svgHeight}`">
      <g :transform="`translate(${offsetX}, 60)`">
        
        <path v-for="(link, index) in links" :key="'link-'+index"
              :d="generateLinkPath(link)"
              fill="none" stroke="#ccc" stroke-width="2"
              :class="{ 'opacity-50': link.target.data.disabled }" />
              
        <text v-for="(link, index) in links" :key="'label-'+index"
              :x="(link.source.x + link.target.x) / 2 - (30 * (link.target.x > link.source.x ? -1 : 1))"
              :y="(link.source.y + link.target.y) / 2 + (NODE_H / 2)"
              font-size="12px" fill="#666" text-anchor="middle"
              :class="{ 'opacity-50': link.target.data.disabled }">
          {{ link.target.data.edge || "" }}
        </text>

        <g v-for="node in nodes" :key="node.data.name"
           :transform="`translate(${node.x - NODE_W / 2}, ${node.y})`"
           @click="handleNodeClick(node)"
           style="cursor: pointer; transition: all 0.2s;"
           :class="{ 'opacity-50': node.data.disabled }">
           
           <rect :width="isLargeNode(node) ? NODE_W : SMALL_NODE_W" 
                 :height="isLargeNode(node) ? NODE_H : SMALL_NODE_H"
                 :x="isLargeNode(node) ? 0 : (NODE_W - SMALL_NODE_W) / 2"
                 :y="isLargeNode(node) ? 0 : (NODE_H - SMALL_NODE_H) / 2"
                 :fill="node.data.type === 'leaf' ? '#d4edda' : '#fff3cd'"
                 stroke="#333" stroke-width="1.5" rx="5" ry="5" />
                 
           <foreignObject 
              :x="isLargeNode(node) ? 0 : (NODE_W - SMALL_NODE_W) / 2" 
              :y="isLargeNode(node) ? 0 : (NODE_H - SMALL_NODE_H) / 2" 
              :width="isLargeNode(node) ? NODE_W : SMALL_NODE_W" 
              :height="isLargeNode(node) ? NODE_H : SMALL_NODE_H">
              <div xmlns="http://www.w3.org/1999/xhtml" 
                   style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 100%; text-align: center; font-size: 12px; font-family: sans-serif; padding: 4px; box-sizing: border-box;">
                  <strong v-if="isLargeNode(node)">DT.ACM-1.{{ node.data.name }}</strong>
                  <strong v-else>{{ node.data.name }}</strong>
                  <span v-if="isLargeNode(node)">{{ node.data.desc }}</span>
              </div>
           </foreignObject>
        </g>
        
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  initialTree: Object,
  deviceId: String
})

// Costanti dimensionali (Mantenute dal tuo codice originale)
const NODE_W = 260
const NODE_H = 70
const SMALL_NODE_W = 100
const SMALL_NODE_H = 40

// Stato per le dimensioni dinamiche
const svgWidth = ref(1000)
const svgHeight = ref(800)
const offsetX = ref(0)

// Helper visivo
const isLargeNode = (node) => node.data.desc && node.data.desc.length > 10

// CALCOLO DELL'ALBERO TRAMITE D3 (La Mente)
const treeLayout = computed(() => {
  // Prepariamo la gerarchia
  const root = d3.hierarchy(props.initialTree)
  
  // Impostiamo il layout D3
  const layout = d3.tree()
    .nodeSize([NODE_W + 30, NODE_H + 40])
    .separation((a, b) => a.parent === b.parent ? 1 : 1.3)
    
  layout(root)
  return root
})

// Estraiamo Nodi e Link per Vue (Le Braccia)
const nodes = computed(() => treeLayout.value.descendants())
const links = computed(() => treeLayout.value.links())

// Funzione per disegnare le linee di collegamento
const generateLinkPath = (link) => {
  const linkGen = d3.linkVertical()
    .x(d => d.x)
    .y(d => d.y + NODE_H / 2)
  return linkGen({
    source: { x: link.source.x, y: link.source.y },
    target: { x: link.target.x, y: link.target.y }
  })
}

// Centratura automatica al caricamento
onMounted(() => {
  const xs = nodes.value.map(d => d.x)
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const treeW = maxX - minX
  
  // Aggiorniamo le dimensioni stimate
  svgWidth.value = treeW + NODE_W * 2
  svgHeight.value = Math.max(...nodes.value.map(d => d.y)) + NODE_H * 3
  
  // Centriamo l'albero calcolando l'offset
  offsetX.value = (svgWidth.value / 2) - (treeW / 2) - minX
})

// Gestione del Click
const handleNodeClick = (node) => {
  if (!node.parent) return; // La root non si clicca
  
  // Scopriamo se è il figlio "Yes" (sinistro) o "No" (destro)
  const isYesChild = node.parent.children[0] === node
  
  console.log(`Cliccato nodo: ${node.data.name}, Risposta: ${isYesChild}`)
  
  // Per ora manteniamo il tuo redirect originale per non rompere il backend
  // In futuro, qui metteremo una fetch() per un aggiornamento invisibile!
  const currentUrl = window.location.href
  window.location.href = `${currentUrl}/updatedt?set=${node.parent.data.name}&value=${isYesChild}`
}
</script>

<style scoped>
.opacity-50 {
  opacity: 0.5;
}
</style>