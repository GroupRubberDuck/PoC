<template>
  <div class="editor-wrapper">
    <header v-if="data" class="tree-header">
      <h2>Requisito: {{ data.requirement }}</h2>
      <p>Asset: <strong>{{ data.asset_name }}</strong></p>
      <p class="text-hint">È possibile modificare le risposte cliccando sui nodi (rettangoli).</p>
    </header>

    <div id="tree-container" ref="treeContainer">
      <svg id="tree-svg" ref="treeSvg"></svg>
    </div>

    <div class="buttons" v-if="data" style="display: flex; gap: 15px; margin-top: 20px;">
      
      <router-link 
        v-if="data.prev_req" 
        :to="`/editor/${$route.params.device_id}/${$route.params.asset_index}/${data.prev_req}`" 
        class="btnBack" style="background: #7f8c8d;">
        Indietro ({{ data.prev_req }})
      </router-link>

      <router-link :to="`/dashboard/${$route.params.device_id}`" class="btnBack" style="background: #2c3e50;">
        Torna alla Dashboard
      </router-link>

      <router-link 
        v-if="data.next_req" 
        :to="`/editor/${$route.params.device_id}/${$route.params.asset_index}/${data.next_req}`" 
        class="btnBack" style="background: #27ae60;">
        Avanti ({{ data.next_req }}) ➡
      </router-link>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as d3 from 'd3'

const route = useRoute()
const data = ref(null)
const treeContainer = ref(null)
const treeSvg = ref(null)

// Costanti originali dal tuo HTML
const NODE_W = 260, NODE_H = 70, SMALL_NODE_W = 100, SMALL_NODE_H = 40;

const fetchTree = async () => {
  const { device_id, asset_index, requirement } = route.params
  const res = await fetch(`/api/dt/${device_id}/${asset_index}/${requirement}`)
  data.value = await res.json()
  await nextTick() // Aspetta che il DOM sia pronto
  drawTree()
}

const drawTree = () => {
  if (!data.value || !treeSvg.value) return

  const svg = d3.select(treeSvg.value)
  svg.selectAll("*").remove()
  const g = svg.append("g")

  const root = d3.hierarchy(data.value.tree_data)

  // Layout verticale con le tue dimensioni originali
  const treeLayout = d3.tree()
    .nodeSize([NODE_W + 30, NODE_H + 40])
    .separation((a, b) => a.parent === b.parent ? 1 : 1.3)

  treeLayout(root)

  // Centratura logica originale
  const containerW = treeContainer.value.clientWidth
  const xs = root.descendants().map(d => d.x)
  const minX = Math.min(...xs), maxX = Math.max(...xs)
  const treeW = maxX - minX
  g.attr("transform", `translate(${containerW / 2 - treeW / 2 - minX}, 60)`)

  // Generatore link verticale
  const linkGen = d3.linkVertical().x(d => d.x).y(d => d.y + NODE_H / 2)

  // Disegno Link
  g.selectAll(".link")
    .data(root.links())
    .join("path")
    .attr("class", d => `link ${d.target.data.disabled ? 'disabled' : ''}`)
    .attr("d", d => linkGen({
      source: { x: d.source.x, y: d.source.y },
      target: { x: d.target.x, y: d.target.y }
    }))
    .attr("fill", "none")
    .attr("stroke", d => d.target.data.disabled ? "#ccc" : "#555")
    .attr("stroke-width", 2)

  // Etichette link (Yes/No)
  g.selectAll(".edge-label")
    .data(root.links())
    .join("text")
    .attr("class", d => `edge-label ${d.target.data.edge.toLowerCase()}`)
    .attr("x", d => (d.source.x + d.target.x) / 2 - (30 * (d.target.x > d.source.x ? -1 : 1)))
    .attr("y", d => (d.source.y + d.target.y) / 2 + NODE_H / 2)
    .text(d => d.target.data.edge || "")
    .style("font-size", "12px")

  // Nodi come rettangoli
  const nodes = g.selectAll(".node")
    .data(root.descendants())
    .join("g")
    .attr("class", d => `node ${d.data.type} ${d.data.disabled ? 'disabled' : ''}`)
    .attr("transform", d => `translate(${d.x - NODE_W / 2}, ${d.y})`)
    .style("cursor", d => d.data.disabled ? "default" : "pointer")

  nodes.append("rect")
    .attr("width", d => d.data.desc.length > 10 ? NODE_W : SMALL_NODE_W)
    .attr("height", d => d.data.desc.length > 10 ? NODE_H : SMALL_NODE_H)
    .attr("x", d => d.data.desc.length > 10 ? 0 : (NODE_W - SMALL_NODE_W) / 2)
    .attr("y", d => d.data.desc.length > 10 ? 0 : (NODE_H - SMALL_NODE_H) / 2)
    .attr("fill", d => {
       if (d.data.disabled) return "#f0f0f0"
       if (d.data.type.startsWith('leaf-pass')) return "#d4edda"
       if (d.data.type.startsWith('leaf-fail')) return "#f8d7da"
       return "#fff"
    })
    .attr("stroke", "#333")

  // Testo multi-linea originale
  nodes.append("text")
    .attr("x", NODE_W / 2)
    .attr("y", NODE_H / 2)
    .attr("text-anchor", "middle")
    .each(function (d) {
        const el = d3.select(this);
        const words = d.data.desc.split(" ");
        const part = Math.ceil(words.length / 3);
        const line1 = words.slice(0, part).join(" ");
        const line2 = words.slice(part, part * 2).join(" ");
        const line3 = words.slice(part * 2).join(" ");
        
        if (line2) {
            el.append("tspan").attr("x", NODE_W / 2).attr("dy", "-1.2em").style("font-weight", "bold").text(d.data.name);
            el.append("tspan").attr("x", NODE_W / 2).attr("dy", "1.2em").text(line1);
            el.append("tspan").attr("x", NODE_W / 2).attr("dy", "1.1em").text(line2);
            el.append("tspan").attr("x", NODE_W / 2).attr("dy", "1.1em").text(line3);
        } else {
            el.text(d.data.name).style("font-weight", "bold");
        }
    });

  // Evento click con logica SPA
  nodes.on("click", (event, d) => {
    event.stopPropagation() // Come nel tuo vecchio codice, evita click doppi
    
    // Rimuoviamo il blocco sui nodi disabilitati! L'unico nodo che non si
    // può cliccare è il nodo radice (perché non ha un genitore a cui rispondere)
    if (!d.parent) return
    
    const isYesChild = d.parent.children[0] === d
    updateNodeValue(d.parent.data.name, isYesChild)
  })
}

const updateNodeValue = async (nodeName, value) => {
  const { device_id, asset_index, requirement } = route.params
  
  try {
    const risposta = await fetch('/api/dt/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id,
        asset_index,
        requirement,
        node_name: nodeName,
        value: value // Invia True se clicchi il ramo Yes, False se No
      })
    })

    if (risposta.ok) {
      // IMPORTANTE: Dopo l'aggiornamento su Flask, richiediamo i nuovi dati.
      // Flask userà D3JSNodeAdapter per ricalcolare quali nodi disabilitare.
      await fetchTree() 
    }
  } catch (err) {
    console.error("Errore durante l'aggiornamento:", err)
  }
}

watch(() => route.params.requirement, (newReq, oldReq) => {
  if (newReq !== oldReq) {
    fetchTree()
  }
})

onMounted(fetchTree)
</script>

<style scoped>
.editor-wrapper {
  display: flex;
  flex-direction: column;
  height: 90vh;
}
#tree-container {
  flex-grow: 1;
  overflow: auto;
  background: #fafafa;
  border: 1px solid #ddd;
}
#tree-svg {
  width: 100%;
  height: 2000px; /* Altezza generosa per scrolling */
}
.text-hint { font-style: italic; color: #666; }
.btnBack { 
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background: #2c3e50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
}
/* Stili per stati specifici */
:deep(.disabled) { opacity: 0.5; }
</style>