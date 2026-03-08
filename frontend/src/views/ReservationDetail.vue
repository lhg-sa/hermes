<template>
  <div class="reservation-detail-container">
    <!-- Header -->
    <div class="detail-header">
      <div class="header-row">
        <div class="back-btn" @click="goBack">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </div>
        <h1 class="header-title">Detalle de Reserva</h1>
        <div class="header-actions">
          <div class="status-badge" :class="getStatusClass(reservation?.estado_reserva)">
            {{ reservation?.estado_formatted }}
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando reserva...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadReservation" class="retry-btn">Reintentar</button>
    </div>

    <!-- Reservation Details -->
    <div v-else-if="reservation" class="detail-content">
      <!-- Customer Info Card -->
      <div class="info-card">
        <div class="card-header">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
          </svg>
          <h2>Cliente</h2>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">Nombre:</span>
            <span class="value">{{ reservation.customer_name || 'N/A' }}</span>
          </div>
          <div class="info-row" v-if="reservation.telefono">
            <span class="label">Teléfono:</span>
            <span class="value">{{ reservation.telefono }}</span>
          </div>
        </div>
      </div>

      <!-- Reservation Info Card -->
      <div class="info-card">
        <div class="card-header">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          <h2>Fechas</h2>
        </div>
        <div class="card-body">
          <div class="dates-grid">
            <div class="date-box">
              <span class="date-label">Entrada</span>
              <span class="date-value">{{ reservation.fecha_entrada_formatted }}</span>
            </div>
            <div class="date-box">
              <span class="date-label">Salida</span>
              <span class="date-value">{{ reservation.fecha_salida_formatted }}</span>
            </div>
            <div class="date-box nights">
              <span class="date-label">Noches</span>
              <span class="date-value">{{ reservation.nights }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Rooms Card -->
      <div class="info-card">
        <div class="card-header">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
          </svg>
          <h2>Habitaciones</h2>
        </div>
        <div class="card-body">
          <div v-for="room in reservation.rooms" :key="room.habitacion" class="room-item">
            <div class="room-number">{{ room.habitacion }}</div>
            <div class="room-details">
              <span class="room-type">Q {{ formatNumber(room.precio_base || 0) }}/noche</span>
              <span class="room-guest" v-if="room.nota">{{ room.nota }}</span>
            </div>
            <div class="room-total" v-if="room.total_estadia">
              Q {{ formatNumber(room.total_estadia) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Notes Card -->
      <div class="info-card" v-if="reservation.notas">
        <div class="card-header">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <h2>Notas</h2>
        </div>
        <div class="card-body">
          <p class="notes-text">{{ reservation.notas }}</p>
        </div>
      </div>

      <!-- Total Card -->
      <div class="info-card total-card">
        <div class="card-body">
          <div class="total-row">
            <span class="total-label">Total</span>
            <span class="total-value">Q {{ formatNumber(reservation.total_global || 0) }}</span>
          </div>
          <div class="total-row" v-if="reservation.total_abonado > 0">
            <span class="total-label">Abonado</span>
            <span class="total-value paid">Q {{ formatNumber(reservation.total_abonado) }}</span>
          </div>
          <div class="total-row" v-if="reservation.total_pendiente > 0">
            <span class="total-label">Pendiente</span>
            <span class="total-value pending">Q {{ formatNumber(reservation.total_pendiente) }}</span>
          </div>
        </div>
      </div>

      <!-- Creation Info -->
      <div class="creation-info">
        <p>Creada: {{ reservation.creation_formatted }}</p>
        <p>ID: {{ reservation.reservation_id }}</p>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
      <router-link to="/availability" class="nav-item">
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
      <router-link to="/reports" class="nav-item active">
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
import { useRouter, useRoute } from 'vue-router'
import { call, logout as frappeLogout } from '../utils/frappe.js'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const error = ref('')
const reservation = ref(null)

const loadReservation = async () => {
  loading.value = true
  error.value = ''
  
  const reservationId = route.params.id
  
  if (!reservationId) {
    error.value = 'ID de reserva no proporcionado'
    loading.value = false
    return
  }
  
  try {
    const result = await call('hermes.api.get_reservation_details', {
      reservation_id: reservationId
    })
    
    if (!result) {
      error.value = 'Reserva no encontrada'
    } else {
      reservation.value = result
    }
  } catch (e) {
    if (e.message === 'SESSION_EXPIRED') {
      router.push('/login')
      return
    }
    error.value = 'Error al cargar la reserva. Intenta de nuevo.'
    console.error(e)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/availability')
}

const logout = async () => {
  await frappeLogout()
  localStorage.removeItem('hermes_token')
  router.push('/login')
}

const getStatusClass = (status) => {
  const classes = {
    'RESERVA PAGADA': 'status-paid',
    'RESERVA SIN PAGO': 'status-unpaid',
    'TENTATIVO': 'status-tentative',
    'NO SHOW': 'status-noshow'
  }
  return classes[status] || 'status-free'
}

const formatNumber = (num) => {
  return num.toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

onMounted(() => {
  loadReservation()
})
</script>

<style scoped>
.reservation-detail-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f0f4f8;
  padding-bottom: 70px;
}

/* Header */
.detail-header {
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

.status-badge {
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-paid {
  background: #fee2e2;
  color: #dc2626;
}

.status-unpaid {
  background: #dbeafe;
  color: #2563eb;
}

.status-tentative {
  background: #fef3c7;
  color: #d97706;
}

.status-noshow {
  background: #f3f4f6;
  color: #4b5563;
}

/* Loading & Error */
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
  border-top-color: #3b82f6;
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
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

/* Content */
.detail-content {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Info Cards */
.info-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.card-header svg {
  width: 20px;
  height: 20px;
  color: #3b82f6;
}

.card-header h2 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.card-body {
  padding: 1rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-size: 0.875rem;
  color: #64748b;
}

.value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
}

/* Dates Grid */
.dates-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.date-box {
  background: #f8fafc;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
}

.date-box.nights {
  grid-column: span 2;
  background: #eff6ff;
}

.date-label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.date-value {
  display: block;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

/* Room Items */
.room-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.room-item:last-child {
  margin-bottom: 0;
}

.room-number {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 700;
}

.room-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.room-type {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
}

.room-guest {
  font-size: 0.75rem;
  color: #64748b;
}

.room-total {
  font-size: 0.875rem;
  font-weight: 600;
  color: #059669;
}

/* Notes */
.notes-text {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

/* Total Card */
.total-card {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.total-card .card-body {
  padding: 1.25rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
}

.total-row:first-child {
  padding-bottom: 0.5rem;
}

.total-label {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.8);
}

.total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.total-value.paid {
  font-size: 1rem;
  color: #86efac;
}

.total-value.pending {
  font-size: 1rem;
  color: #fde047;
}

/* Creation Info */
.creation-info {
  text-align: center;
  padding: 1rem;
}

.creation-info p {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0.25rem 0;
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
</style>