import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import CaseDetails from '../views/CaseDetails.vue';
const routes: Array<RouteRecordRaw> = [
    { path: '/case-details', name: 'CaseDetails', component: CaseDetails },
  ]
  
  const router = createRouter({
    history: createWebHistory(process.env.BASE_URL),
    routes
  })
  
  export default router;