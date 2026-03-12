<template>
  <div class="availability-container">
    <!-- Top Navigation Header -->
    <div class="top-header">
      <!-- Date Navigation Bar -->
      <div class="date-nav">
        <button class="nav-btn" @click="prevWeek">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>
        <div class="date-info" @click="openMonthYearSelector">
          <p class="month-year">{{ weekInfo.month }} {{ weekInfo.year }}</p>
          <p class="week-num">{{ weekInfo.weeks }}</p>
          <svg class="dropdown-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </div>
        <button class="nav-btn" @click="nextWeek">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
        <button class="current-week-btn" @click="goToToday">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="btn-icon">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          Semana Actual
        </button>
      </div>
      
      <!-- Month/Year Selector Modal -->
      <div v-if="showMonthYearSelector" class="modal-overlay" @click="closeMonthYearSelector">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Seleccionar Mes y Año</h3>
            <button class="modal-close" @click="closeMonthYearSelector">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="selector-group">
              <label>Año</label>
              <select v-model="selectedYear" class="selector-input">
                <option v-for="year in availableYears" :key="year" :value="year">
                  {{ year }}
                </option>
              </select>
            </div>
            <div class="selector-group">
              <label>Mes</label>
              <select v-model="selectedMonth" class="selector-input">
                <option v-for="(month, index) in months" :key="index" :value="index">
                  {{ month }}
                </option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="modal-btn cancel" @click="closeMonthYearSelector">Cancelar</button>
            <button class="modal-btn confirm" @click="applyMonthYear">Ir</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingState v-if="loading" :message="t('availability.loading', 'Cargando disponibilidad...')" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" :retry="loadData" />

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
              @click="onCellClick(room, day, roomName)"
            >
              <div 
                class="status-cell"
                :class="getStatusClass(room.days[day.date]?.status)"
              ></div>
            </td>
          </tr>
        </tbody>
        <tfoot v-if="showTotals">
          <tr class="totals-row occupied">
            <td class="sticky-col total-label">Ocupadas</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ displayTotals[day.date]?.occupied || 0 }}
            </td>
          </tr>
          <tr class="totals-row free">
            <td class="sticky-col total-label">Libres</td>
            <td v-for="day in weekInfo.days" :key="day.date" class="total-cell">
              {{ displayTotals[day.date]?.free || 0 }}
            </td>
          </tr>
          <tr class="totals-toggle-row">
            <td :colspan="weekInfo.days.length + 1" class="totals-toggle-cell">
              <button class="toggle-totals-btn hide" @click="showTotals = false">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/>
                </svg>
                Ocultar Totales
              </button>
            </td>
          </tr>
        </tfoot>
        <tfoot v-else>
          <tr class="totals-toggle-row">
            <td :colspan="weekInfo.days.length + 1" class="totals-toggle-cell">
              <button class="toggle-totals-btn" @click="showTotals = true">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
                Mostrar Totales
              </button>
            </td>
          </tr>
        </tfoot>
      </table>
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

    <!-- Bottom Navigation -->
    <BottomNavigation active="availability" @logout="logout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from '../utils/frappe.js'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'
import BottomNavigation from '../components/BottomNavigation.vue'
import LoadingState from '../components/LoadingState.vue'
import ErrorState from '../components/ErrorState.vue'

const router = useRouter()
const { t } = useI18n()
const { logout } = useAuth()

const loading = ref(true)
const error = ref('')
const rooms = ref({})
const totals = ref({})
const weekInfo = ref({ days: [], month: '', year: '', weeks: '' })
const startDate = ref(null)

// Month/Year selector state
const showMonthYearSelector = ref(false)
const selectedYear = ref(new Date().getFullYear())
const selectedMonth = ref(new Date().getMonth())
const months = [
  t('months.january', 'Enero'),
  t('months.february', 'Febrero'),
  t('months.march', 'Marzo'),
  t('months.april', 'Abril'),
  t('months.may', 'Mayo'),
  t('months.june', 'Junio'),
  t('months.july', 'Julio'),
  t('months.august', 'Agosto'),
  t('months.september', 'Septiembre'),
  t('months.october', 'Octubre'),
  t('months.november', 'Noviembre'),
  t('months.december', 'Diciembre')
]
const availableYears = ref([])

// Generate available years (current year and next year only)
const generateYears = () => {
  const currentYear = new Date().getFullYear()
  availableYears.value = [currentYear, currentYear + 1]
}

// Totals visibility state
const showTotals = ref(false)

// Computed totals for display (grouped)
const displayTotals = computed(() => {
  const result = {}
  for (const [date, data] of Object.entries(totals.value)) {
    result[date] = {
      occupied: (data.tentative || 0) + (data.unpaid || 0) + (data.paid || 0) + (data.noshow || 0),
      free: data.free || 0
    }
  }
  return result
})

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

const openMonthYearSelector = () => {
  // Set current selection based on current view
  if (startDate.value) {
    const current = new Date(startDate.value)
    selectedYear.value = current.getFullYear()
    selectedMonth.value = current.getMonth()
  } else {
    const today = new Date()
    selectedYear.value = today.getFullYear()
    selectedMonth.value = today.getMonth()
  }
  generateYears()
  showMonthYearSelector.value = true
}

const closeMonthYearSelector = () => {
  showMonthYearSelector.value = false
}

const applyMonthYear = () => {
  // Get the Monday of the first week of the selected month
  const selected = new Date(selectedYear.value, selectedMonth.value, 1)
  const dayOfWeek = selected.getDay()
  const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
  selected.setDate(selected.getDate() + daysToMonday)
  
  startDate.value = selected.toISOString().split('T')[0]
  showMonthYearSelector.value = false
  loadData()
}

const goBack = () => {
  router.push('/home')
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

const onCellClick = (room, day, roomName) => {
  const dayData = room.days[day.date]
  
  // If cell is available (green/free), navigate to create reservation with dates
  if (!dayData?.reservation && dayData?.status === 'free') {
    // Calculate checkout date (one day after checkin)
    const checkinDate = new Date(day.date)
    const checkoutDate = new Date(checkinDate)
    checkoutDate.setDate(checkoutDate.getDate() + 1)
    
    const checkinStr = checkinDate.toISOString().split('T')[0]
    const checkoutStr = checkoutDate.toISOString().split('T')[0]
    
    // Navigate to reservations with pre-filled dates and room
    router.push({
      path: '/reservations',
      query: {
        fecha_entrada: checkinStr,
        fecha_salida: checkoutStr,
        habitacion: roomName
      }
    })
    return
  }
  
  // If there's a reservation, navigate to detail
  if (dayData?.reservation) {
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
  background: #f0f4f8;
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
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
  transition: background 0.2s;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.125rem;
}

.date-info:hover {
  background: rgba(19, 109, 236, 0.1);
}

.dropdown-icon {
  width: 16px;
  height: 16px;
  color: #64748b;
  margin-top: 2px;
}

.month-year {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2563eb;
}

.week-num {
  font-size: 0.75rem;
  color: #64748b;
}

/* Current Week Button */
.current-week-btn-container {
  padding: 0 1rem 0.75rem;
  display: flex;
  justify-content: center;
}

.current-week-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.current-week-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.4);
  background: #2563eb;
}

.current-week-btn:active {
  transform: translateY(0);
}

.current-week-btn .btn-icon {
  width: 16px;
  height: 16px;
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
  background: white;
  padding: 0.375rem 0.625rem;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-item span {
  color: #1e293b;
}

/* Status Colors - Light Day Theme */
.status-tentative {
  background: #fbbf24;
}

.status-unpaid {
  background: #60a5fa;
}

.status-paid {
  background: #f87171;
}

.status-noshow {
  background: #9ca3af;
}

.status-free {
  background: #4ade80;
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

/* Month/Year Selector Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 320px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  color: #64748b;
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.selector-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.selector-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.selector-input:focus {
  outline: none;
  border-color: #136dec;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #e2e8f0;
}

.modal-btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-btn.cancel {
  background: #f1f5f9;
  color: #64748b;
  border: none;
}

.modal-btn.cancel:hover {
  background: #e2e8f0;
}

.modal-btn.confirm {
  background: linear-gradient(135deg, #136dec 0%, #0d5bb8 100%);
  color: white;
  border: none;
}

.modal-btn.confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(19, 109, 236, 0.3);
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
  padding-left: 0.5rem;
  font-size: 0.625rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  min-width: 100px;
  max-width: 100px;
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
  background: #3b82f6;
  position: relative;
}

.is-today::after {
  content: 'HOY';
  position: absolute;
  top: 2px;
  right: 4px;
  font-size: 0.5rem;
  font-weight: 700;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 4px;
  border-radius: 2px;
}

.is-today .day-name {
  color: white;
}

.today-number {
  color: white;
  font-size: 1rem;
}

/* Room Name */
.room-name {
  padding: 0.5rem;
  font-size: 0.625rem;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  border-right: 1px solid #e2e8f0;
  min-width: 100px;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
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
  background: white;
}

.totals-row.occupied .total-label {
  background: white;
  color: #dc2626;
  border: 2px solid #f87171;
  border-right: 1px solid #e2e8f0;
}

.totals-row.free .total-label {
  background: white;
  color: #16a34a;
  border: 2px solid #4ade80;
  border-right: 1px solid #e2e8f0;
}

.total-label {
  padding: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-right: 1px solid #e2e8f0;
  min-width: 70px;
  max-width: 70px;
}

.total-cell {
  padding: 0.5rem 0.25rem;
  text-align: center;
  font-size: 0.625rem;
  font-weight: 700;
  border-right: 1px solid #e2e8f0;
}

/* Totals Toggle */
.totals-toggle-row {
  background: white;
}

.totals-toggle-cell {
  padding: 0.5rem;
  text-align: center;
}

.toggle-totals-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  background: white;
  color: #3b82f6;
  border: 2px solid #3b82f6;
  border-radius: 6px;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
}

.toggle-totals-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
  background: #eff6ff;
}

.toggle-totals-btn svg {
  width: 14px;
  height: 14px;
}

.toggle-totals-btn.hide {
  background: white;
  color: #64748b;
  border-color: #64748b;
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
  color: #3b82f6;
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
  
  .totals-toggle-row {
    background: #ffffff;
  }
  
  .toggle-totals-btn {
    background: #ffffff;
    color: #3b82f6;
    border-color: #3b82f6;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  }
  
  .toggle-totals-btn:hover {
    background: #eff6ff;
  }
  
  .toggle-totals-btn.hide {
    background: #ffffff;
    color: #64748b;
    border-color: #64748b;
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
  
  .legend-item {
    background: #334155;
  }
  
  .legend-item span {
    color: #f1f5f9;
  }
  
  .current-week-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  }
  
  .is-today {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  }
  
  .totals-row.occupied .total-label,
  .totals-row.free .total-label {
    background: #ffffff;
  }
  
  .modal-content {
    background: #1e293b;
  }
  
  .modal-header {
    border-color: #334155;
  }
  
  .modal-header h3 {
    color: #f1f5f9;
  }
  
  .modal-close {
    color: #94a3b8;
  }
  
  .selector-group label {
    color: #94a3b8;
  }
  
  .selector-input {
    background: #334155;
    border-color: #475569;
    color: #f1f5f9;
  }
  
  .selector-input:focus {
    border-color: #3b82f6;
  }
  
  .modal-footer {
    border-color: #334155;
  }
  
  .modal-btn.cancel {
    background: #334155;
    color: #94a3b8;
  }
  
  .modal-btn.cancel:hover {
    background: #475569;
  }
}
</style>