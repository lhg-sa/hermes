import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './views/Login.vue'
import Home from './views/Home.vue'
import Availability from './views/Availability.vue'
import Reservations from './views/Reservations.vue'
import ReservationDetail from './views/ReservationDetail.vue'
import Reports from './views/Reports.vue'
import { checkAuth } from './utils/frappe.js'

// Shared styles
import './styles/variables.css'
import './styles/common.css'
import './theme/index.css'

// Router configuration
const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/availability',
    name: 'Availability',
    component: Availability,
    meta: { requiresAuth: true }
  },
  {
    path: '/reservations',
    name: 'Reservations',
    component: Reservations,
    meta: { requiresAuth: true }
  },
  {
    path: '/reservation/:id',
    name: 'ReservationDetail',
    component: ReservationDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/hermes/'),
  routes
})

// Auth guard - verify Frappe session
router.beforeEach(async (to, from, next) => {
  // Check localStorage first for quick redirect
  const hasLocalToken = localStorage.getItem('hermes_token')
  
  if (to.meta.requiresAuth) {
    // Protected route - verify session with Frappe
    const { authenticated } = await checkAuth()
    if (authenticated) {
      next()
    } else {
      // Session expired or not logged in
      localStorage.removeItem('hermes_token')
      localStorage.removeItem('hermes_user')
      next('/login')
    }
  } else if (to.path === '/login' && hasLocalToken) {
    // Already has local token, verify session
    const { authenticated } = await checkAuth()
    if (authenticated) {
      next('/availability')
    } else {
      localStorage.removeItem('hermes_token')
      localStorage.removeItem('hermes_user')
      next()
    }
  } else if (to.path === '/') {
    const { authenticated } = await checkAuth()
    next(authenticated ? '/availability' : '/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.mount('#app')
