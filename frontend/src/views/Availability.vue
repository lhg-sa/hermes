<template>
  <div class="availability-container">
    <!-- Top Navigation Header -->
    <div class="top-header">
      <div class="header-row">
        <div class="back-btn" @click="goBack">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </div>
        <h1 class="header-title">Disponibilidad</h1>
        <div class="header-actions">
          <button class="icon-btn" @click="goToToday">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
          </button>
        </div>
      </div>
      
      <!-- Date Navigation Bar -->
      <div class="date-nav">
        <button class="nav-btn" @click="prevWeek">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <div class="date-info">
          <p class="month-year">{{ weekInfo.month }} {{ weekInfo.year }}</p>
          <p class="week-num">{{ weekInfo.weeks }}</p>
        </div>
        <button class="nav-btn" @click="nextWeek">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-item">
        <div class="legend-color status-tentative"></div>
        <span>Tentativo</span>
      </div>
      <div class="legend-item">
        <div class="legend-color status-unpaid"></div>
        <span>Sin Pago</span>
      </div>
      <div class="legend-item">
        <div class="legend-color status-paid"></div>
        <span>Pagada</span>
      </div>
      <div class="legend-item">
        <div class="legend-color status-noshow"></div>
        <span>No Show</span>
      </div>
      <div class="legend-item">
        <div class="legend-color status-free"></div>
        <span>Libre</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando disponibilidad...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">Reintentar</button>
    </div>

    <!-- Availability Grid -->
    <div v-else class="grid-container">
      <table class="availability-table">
        <thead>
          <tr>
            <th class="sticky-col header-cell rooms-header">HABITACIONES</th>
            <th 
              v-for="day in weekInfo.days" 
              :key="day.date"
              class="header-cell"
              :class="{ 'is-today': day.is_today }"
            >
              <span class="day-name">{{ day.day_name }}</span>
              <span class="day-number" :class="{ 'today-number': day.is_today }">{{ day.day_number }}</span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(room, roomName) in rooms" :key="roomName">
            <td class="sticky-col room-name">{{ room.full_name }}</td>
            <td 
              v-for="day in weekInfo.days" 
              :key="day.date"
              class="cell"
              @click="onCellClick(room, day)"
            >
              <div 
                class="status-cell"
                :class="getStatusClass(room.days[day.date]?.status)"
              ></div>
            </td>
          </tr>
        </tbody>
        <tfoot>
          <tr class="totals-row tentative">
            <td class="sticky-col total-label">Tentativo</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ totals[day.date]?.tentative || 0 }}
            </td>
          </tr>
          <tr class="totals-row unpaid">
            <td class="sticky-col total-label">Reserva Sin Pago</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ totals[day.date]?.unpaid || 0 }}
            </td>
          </tr>
          <tr class="totals-row paid">
            <td class="sticky-col total-label">Reserva Pagada</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ totals[day.date]?.paid || 0 }}
            </td>
          </tr>
          <tr class="totals-row noshow">
            <td class="sticky-col total-label">No Show</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ totals[day.date]?.noshow || 0 }}
            </td>
          </tr>
          <tr class="totals-row free">
            <td class="sticky-col total-label">Libres</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ totals[day.date]?.free || 0 }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/availability" class="nav-item active">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
        <span>Disponibilidad</span>
      </router-link>
      <router-link to="/reservations" class="nav-item">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <span>Reservas</span>
      </router-link>
      <router-link to="/reports" class="nav-item">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <span>Reportes</span>
      </router-link>
      <button class="nav-item" @click="logout">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
        </svg>
        <span>Logout</span>
      </button>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call, logout as frappeLogout } from '../utils/frappe.js'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const rooms = ref({})
const totals = ref({})
const weekInfo = ref({ days: [], month: '', year: '', weeks: '' })
const startDate = ref(null)

const loadData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await call('hermes.api.get_week_availability', {
      start_date: startDate.value
    })
    
    rooms.value = result.rooms
    totals.value = result.totals
    weekInfo.value = result.week_info
    startDate.value = result.start_date
  } catch (e) {
    if (e.message === 'SESSION_EXPIRED') {
      // Redirect to login
      router.push('/login')
      return
    }
    error.value = 'Error al cargar datos. Intenta de nuevo.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const prevWeek = () => {
  if (startDate.value) {
    const current = new Date(startDate.value)
    current.setDate(current.getDate() - 7)
    startDate.value = current.toISOString().split('T')[0]
    loadData()
  }
}

const nextWeek = () => {
  if (startDate.value) {
    const current = new Date(startDate.value)
    current.setDate(current.getDate() + 7)
    startDate.value = current.toISOString().split('T')[0]
    loadData()
  }
}

const goToToday = () => {
  startDate.value = null
  loadData()
}

const goBack = () => {
  router.push('/home')
}

const logout = async () => {
  await frappeLogout()
  localStorage.removeItem('hermes_token')
  router.push('/login')
}

const getStatusClass = (status) => {
  const classes = {
    'tentative': 'status-tentative',
    'unpaid': 'status-unpaid',
    'paid': 'status-paid',
    'noshow': 'status-noshow',
    'free': 'status-free'
  }
  return classes[status] || 'status-free'
}

const onCellClick = (room, day) => {
  const dayData = room.days[day.date]
  if (dayData?.reservation) {
    // Navigate to reservation detail
    router.push(`/reservation/${dayData.reservation.id}`)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.availability-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f6f7f8;
  padding-bottom: 70px;
}

/* Header Styles */
.top-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: white;
  border-bottom: 1px solid #e2e8f0;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #1e293b;
}

.back-btn svg {
  width: 24px;
  height: 24px;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
}

.icon-btn svg {
  width: 24px;
  height: 24px;
}

/* Date Navigation */
.date-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem 0.75rem;
}

.nav-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
}

.nav-btn svg {
  width: 20px;
  height: 20px;
}

.date-info {
  text-align: center;
}

.month-year {
  font-size: 0.875rem;
  font-weight: 600;
  color: #136dec;
}

.week-num {
  font-size: 0.75rem;
  color: #64748b;
}

/* Legend */
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

/* Status Colors */
.status-tentative {
  background: #f59e0b;
}

.status-unpaid {
  background: #3b82f6;
}

.status-paid {
  background: #ef4444;
}

.status-noshow {
  background: #6b7280;
}

.status-free {
  background: #22c55e;
}

/* Loading & Error States */
.loading-state,
.error-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #136dec;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #136dec;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

/* Grid Container */
.grid-container {
  flex: 1;
  overflow-x: auto;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.availability-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

/* Sticky Column */
.sticky-col {
  position: sticky;
  left: 0;
  z-index: 10;
  background: white;
}

/* Header Cells */
.header-cell {
  padding: 0.75rem 0.5rem;
  text-align: center;
  border-right: 1px solid #e2e8f0;
  background: #f8fafc;
  min-width: 50px;
}

.rooms-header {
  text-align: left;
  padding-left: 1rem;
  font-size: 0.625rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  min-width: 140px;
}

.day-name {
  display: block;
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
}

.day-number {
  display: block;
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
}

.is-today {
  background: rgba(19, 109, 236, 0.1);
}

.is-today .day-name {
  color: #136dec;
}

.today-number {
  color: #136dec;
}

/* Room Name */
.room-name {
  padding: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  border-right: 1px solid #e2e8f0;
}

/* Status Cells */
.cell {
  padding: 0.25rem;
  border-right: 1px solid #e2e8f0;
  cursor: pointer;
}

.status-cell {
  height: 40px;
  border-radius: 2px;
  transition: transform 0.1s;
}

.cell:active .status-cell {
  transform: scale(0.95);
}

/* Totals */
.totals-row {
  background: #f8fafc;
}

.totals-row.tentative .total-label {
  color: #f59e0b;
}

.totals-row.unpaid .total-label {
  color: #3b82f6;
}

.totals-row.paid .total-label {
  color: #ef4444;
}

.totals-row.noshow .total-label {
  color: #6b7280;
}

.totals-row.free .total-label {
  color: #22c55e;
}

.total-label {
  padding: 0.75rem 1rem;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-right: 1px solid #e2e8f0;
}

.total-cell {
  padding: 0.75rem 0.5rem;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 700;
  border-right: 1px solid #e2e8f0;
}

/* Bottom Navigation */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #e2e8f0;
  display: flex;
  z-index: 50;
  padding-bottom: env(safe-area-inset-bottom);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: transparent;
  border: none;
  cursor: pointer;
}

.nav-item svg {
  width: 24px;
  height: 24px;
  margin-bottom: 0.25rem;
}

.nav-item.active {
  color: #136dec;
}

.nav-item.active svg {
  stroke-width: 2.5;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
  .availability-container {
    background: #101822;
  }
  
  .top-header {
    background: #1e293b;
    border-color: #334155;
  }
  
  .back-btn,
  .header-title {
    color: #f1f5f9;
  }
  
  .icon-btn {
    color: #94a3b8;
  }
  
  .grid-container {
    background: #1e293b;
    border-color: #334155;
  }
  
  .header-cell {
    background: #334155;
    border-color: #334155;
  }
  
  .day-number {
    color: #f1f5f9;
  }
  
  .room-name {
    background: #1e293b;
    color: #f1f5f9;
    border-color: #334155;
  }
  
  .cell {
    border-color: #334155;
  }
  
  .totals-row {
    background: #334155;
  }
  
  .total-label,
  .total-cell {
    border-color: #334155;
  }
  
  .bottom-nav {
    background: #1e293b;
    border-color: #334155;
  }
  
  .nav-item {
    color: #64748b;
  }
  
  .nav-item.active {
    color: #3b82f6;
  }
}
</style>