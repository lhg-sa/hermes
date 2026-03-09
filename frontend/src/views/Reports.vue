<template>
  <div class="reports-container">
    <!-- Header -->
    <div class="top-header">
      <h1 class="header-title">Reportes</h1>
    </div>

    <!-- Loading State -->
    <LoadingState v-if="loading" :message="'Cargando reservas...'" />

    <!-- Error State -->
    <ErrorState v-else-if="error" :message="error" :retry="loadReservations" />

    <!-- Content -->
    <div v-else class="reports-content">
      <div class="section-title">Últimas Reservas</div>
      
      <div v-if="recentReservations.length === 0" class="empty-state">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="empty-icon">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
        </svg>
        <p>No hay reservas aún</p>
      </div>

      <!-- Reservations List -->
      <div v-else class="reservations-list">
        <div 
          v-for="reservation in recentReservations" 
          :key="reservation.name"
          class="reservation-card"
          @click="viewReservation(reservation)"
        >
          <div class="reservation-header">
            <span class="reservation-id">{{ reservation.name }}</span>
            <span class="reservation-status" :class="getStatusClass(reservation.estado_reserva)">
              {{ formatStatus(reservation.estado_reserva) }}
            </span>
          </div>
          <div class="reservation-details">
            <div class="detail-row">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="detail-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              <span>{{ formatDate(reservation.fecha_entrada) }} → {{ formatDate(reservation.fecha_salida) }}</span>
            </div>
            <div class="detail-row">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="detail-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              </svg>
              <span>{{ reservation.habitacion }}</span>
            </div>
            <div class="detail-row" v-if="reservation.customer_name">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="detail-icon">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              <span>{{ reservation.customer_name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <BottomNavigation active="reports" @logout="logout" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from '../utils/frappe.js'
import { useAuth } from '../composables/useAuth'
import BottomNavigation from '../components/BottomNavigation.vue'
import LoadingState from '../components/LoadingState.vue'
import ErrorState from '../components/ErrorState.vue'

const router = useRouter()
const { logout } = useAuth()

const loading = ref(true)
const error = ref('')
const recentReservations = ref([])

const loadReservations = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await call('hermes.api.get_recent_reservations', {
      limit: 5
    })
    recentReservations.value = result || []
  } catch (e) {
    if (e.message === 'SESSION_EXPIRED') {
      router.push('/login')
      return
    }
    error.value = 'Error al cargar reservas'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-GT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const formatStatus = (status) => {
  const statusMap = {
    'TENTATIVO': 'Tentativo',
    'RESERVA SIN PAGO': 'Sin Pago',
    'RESERVA PAGADA': 'Pagada',
    'CHECKIN': 'Check-in',
    'CHECKOUT': 'Check-out',
    'CANCELADO': 'Cancelado',
    'NOSHOW': 'No Show'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classes = {
    'TENTATIVO': 'status-tentative',
    'RESERVA SIN PAGO': 'status-unpaid',
    'RESERVA PAGADA': 'status-paid',
    'CHECKIN': 'status-checkin',
    'CHECKOUT': 'status-checkout',
    'CANCELADO': 'status-cancelled',
    'NOSHOW': 'status-noshow'
  }
  return classes[status] || 'status-default'
}

const viewReservation = (reservation) => {
  router.push(`/reservation/${reservation.name}`)
}

onMounted(() => {
  loadReservations()
})
</script>

<style scoped>
.reports-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f0f4f8;
  padding-bottom: 70px;
}

.top-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.reports-content {
  flex: 1;
  padding: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-icon {
  width: 48px;
  height: 48px;
  margin-bottom: 1rem;
}

.reservations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reservation-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.reservation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.reservation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.reservation-id {
  font-weight: 600;
  font-size: 0.875rem;
  color: #1e293b;
}

.reservation-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.status-tentative {
  background: #fef3c7;
  color: #92400e;
}

.status-unpaid {
  background: #fee2e2;
  color: #dc2626;
}

.status-paid {
  background: #dcfce7;
  color: #16a34a;
}

.status-checkin {
  background: #dbeafe;
  color: #2563eb;
}

.status-checkout {
  background: #e0e7ff;
  color: #4f46e5;
}

.status-cancelled {
  background: #f1f5f9;
  color: #64748b;
}

.status-noshow {
  background: #fee2e2;
  color: #991b1b;
}

.status-default {
  background: #f1f5f9;
  color: #64748b;
}

.reservation-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.detail-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
</style>
