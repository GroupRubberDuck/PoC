import { createRouter, createWebHistory } from 'vue-router'
import ImportView from './views/Import.vue'
import DashboardView from './views/Dashboard.vue'
import ReportView from './views/Report.vue'

const routes = [
  {
    path: '/',
    name: 'Import',
    component: ImportView
  },
  {
    // Il parametro :id ci permette di avere URL dinamici come /dashboard/123
    path: '/dashboard/:id',
    name: 'Dashboard',
    component: DashboardView
  },
  {
    path: '/editor/:device_id/:asset_index/:requirement',
    name: 'Editor',
    component: () => import('./views/TreeEditor.vue')
  },
  {
    path: '/report/:id',
    name: 'Report',
    component: ReportView
  }
]

export const router = createRouter({
  // createWebHistory rimuove il fastidioso '#' dagli URL
  history: createWebHistory(),
  routes
})