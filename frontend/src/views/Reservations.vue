<template>
  <div class="reservations-container">
    <!-- Header -->
    <div class="top-header">
      <h1 class="header-title">Nueva Reserva</h1>
    </div>

    <!-- Form -->
    <div class="form-content">
      <!-- Customer Selection -->
      <div class="form-group">
        <label>Cliente *</label>
        <div class="customer-search">
          <input 
            type="text" 
            v-model="customerSearch" 
            @input="onCustomerInput"
            placeholder="Escribe el nombre del cliente..."
            class="form-input"
            :disabled="!!form.cliente"
          />
          <!-- Dropdown -->
          <div v-if="showDropdown && customerSearch.length >= 2" class="customer-results">
            <!-- Loading -->
            <div v-if="isLoadingCustomers" class="customer-option loading">
              <div class="btn-spinner small"></div>
              <span>Buscando...</span>
            </div>
            <!-- Results -->
            <template v-else>
              <!-- Existing customers -->
              <div 
                v-for="customer in filteredCustomers" 
                :key="customer.name"
                class="customer-option"
                @click="selectCustomer(customer)"
              >
                <div class="customer-option-main">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="customer-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  <span>{{ customer.customer_name }}</span>
                </div>
                <span class="customer-label">Existente</span>
              </div>
              <!-- No results message -->
              <div v-if="filteredCustomers.length === 0 && !isCreatingCustomer" class="customer-option no-results">
                <span>No se encontraron clientes</span>
              </div>
              <!-- Create new customer option -->
              <div 
                v-if="!hasExactMatch && !isCreatingCustomer"
                class="customer-option create-new"
                @click="createNewCustomer"
              >
                <div class="customer-option-main">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="customer-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                  </svg>
                  <span>Crear: "{{ customerSearch }}"</span>
                </div>
                <span class="customer-label new">Nuevo</span>
              </div>
              <!-- Creating spinner -->
              <div v-if="isCreatingCustomer" class="customer-option loading">
                <div class="btn-spinner small"></div>
                <span>Creando cliente...</span>
              </div>
            </template>
          </div>
        </div>
        <!-- Selected customer -->
        <div v-if="form.cliente" class="selected-customer">
          <span>{{ form.customer_name }}</span>
          <button class="clear-btn" @click="clearCustomer" type="button">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Dates -->
      <div class="dates-section">
        <label>Fechas *</label>
        <div class="dates-inputs">
          <div class="date-field">
            <input type="date" v-model="form.fecha_entrada" class="form-input date-input" />
          </div>
          <span class="date-separator">→</span>
          <div class="date-field">
            <input type="date" v-model="form.fecha_salida" class="form-input date-input" />
          </div>
        </div>
        <!-- Quick date selection -->
        <div class="quick-dates">
          <button type="button" class="quick-btn" @click="setToday">Hoy</button>
          <button type="button" class="quick-btn" @click="setTomorrow">Mañana</button>
          <button type="button" class="quick-btn" @click="setThisWeekend">Fin de semana</button>
        </div>
        <div v-if="nights > 0" class="nights-info-inline">
          <span>{{ nights }} noche(s)</span>
        </div>
      </div>

      <!-- Room Selection -->
      <div class="form-group">
        <label>Habitacion *</label>
        <select v-model="form.habitacion" class="form-input" @change="updateRoomPrice" :disabled="!form.fecha_entrada || !form.fecha_salida">
          <option value="">{{ form.fecha_entrada && form.fecha_salida ? 'Seleccionar habitacion' : 'Seleccione fechas primero' }}</option>
          <option v-for="room in availableRooms" :key="room.name" :value="room.name">
            {{ room.full_name }} - Q{{ formatNumber(room.precio_base) }}/noche
          </option>
        </select>
        <div v-if="form.fecha_entrada && form.fecha_salida && availableRooms.length === 0 && nights > 0" class="no-rooms-message">
          No hay habitaciones disponibles para estas fechas
        </div>
      </div>

      <!-- Price Summary -->
      <div v-if="form.habitacion && nights > 0" class="price-card">
        <div class="price-row">
          <span>Habitacion:</span>
          <span>{{ getRoomName() }}</span>
        </div>
        <div class="price-row">
          <span>Precio por noche:</span>
          <span>Q {{ formatNumber(form.precio_base) }}</span>
        </div>
        <div class="price-row">
          <span>Noches:</span>
          <span>{{ nights }}</span>
        </div>
        <div class="price-row total">
          <span>Total:</span>
          <span>Q {{ formatNumber(form.precio_base * nights) }}</span>
        </div>
      </div>

      <!-- Status -->
      <div class="form-group">
        <label>Estado</label>
        <select v-model="form.estado_reserva" class="form-input">
          <option value="TENTATIVO">Tentativo</option>
          <option value="RESERVA SIN PAGO">Reserva Sin Pago</option>
          <option value="RESERVA PAGADA">Reserva Pagada</option>
        </select>
      </div>

      <!-- Notes -->
      <div class="form-group">
        <label>Notas</label>
        <textarea v-model="form.notas" class="form-input" rows="3" placeholder="Notas adicionales..."></textarea>
      </div>

      <!-- Save Button -->
      <button class="save-btn" @click="saveReservation" :disabled="saving || !isFormValid" type="button">
        <span v-if="saving" class="btn-spinner"></span>
        <span v-else>Guardar Reserva</span>
      </button>
    </div>

    <!-- Bottom Navigation -->
    <BottomNavigation active="reservations" @logout="logout" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { call } from '../utils/frappe.js'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'
import { useFormatters } from '../composables/useFormatters'
import BottomNavigation from '../components/BottomNavigation.vue'

const router = useRouter()
const { t } = useI18n()
const { logout } = useAuth()
const { formatNumber, formatCurrency } = useFormatters()

const saving = ref(false)
const customerSearch = ref('')
const filteredCustomers = ref([])
const showDropdown = ref(false)
const isLoadingCustomers = ref(false)
const isCreatingCustomer = ref(false)
const availableRooms = ref([])

const form = ref({
  cliente: '',
  customer_name: '',
  fecha_entrada: '',
  fecha_salida: '',
  habitacion: '',
  precio_base: 0,
  estado_reserva: 'TENTATIVO',
  notas: ''
})

const nights = computed(() => {
  if (form.value.fecha_entrada && form.value.fecha_salida) {
    const start = new Date(form.value.fecha_entrada)
    const end = new Date(form.value.fecha_salida)
    const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
    return diff > 0 ? diff : 0
  }
  return 0
})

const hasExactMatch = computed(() => {
  const searchLower = customerSearch.value.toLowerCase().trim()
  return filteredCustomers.value.some(c => 
    c.customer_name.toLowerCase() === searchLower
  )
})

const isFormValid = computed(() => {
  return form.value.cliente && 
         form.value.fecha_entrada && 
         form.value.fecha_salida && 
         form.value.habitacion &&
         nights.value > 0
})

const loadAvailableRooms = async () => {
  // Only load if both dates are set
  if (!form.value.fecha_entrada || !form.value.fecha_salida) {
    availableRooms.value = []
    return
  }
  
  try {
    const result = await call('hermes.api.get_available_rooms_for_dates', {
      fecha_entrada: form.value.fecha_entrada,
      fecha_salida: form.value.fecha_salida
    })
    availableRooms.value = result || []
    
    // Clear selected room if it's no longer available
    if (form.value.habitacion && !availableRooms.value.find(r => r.name === form.value.habitacion)) {
      form.value.habitacion = ''
      form.value.precio_base = 0
    }
  } catch (e) {
    console.error('Error loading rooms:', e)
    availableRooms.value = []
  }
}

// Quick date selection functions
const formatDate = (date) => {
  return date.toISOString().split('T')[0]
}

const setToday = () => {
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  form.value.fecha_entrada = formatDate(today)
  form.value.fecha_salida = formatDate(tomorrow)
}

const setTomorrow = () => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  const dayAfter = new Date(tomorrow)
  dayAfter.setDate(dayAfter.getDate() + 1)
  form.value.fecha_entrada = formatDate(tomorrow)
  form.value.fecha_salida = formatDate(dayAfter)
}

const setThisWeekend = () => {
  const today = new Date()
  const dayOfWeek = today.getDay()
  // Find next Saturday (day 6)
  const saturday = new Date(today)
  const daysUntilSaturday = (6 - dayOfWeek + 7) % 7 || 7
  saturday.setDate(today.getDate() + daysUntilSaturday)
  const sunday = new Date(saturday)
  sunday.setDate(saturday.getDate() + 1)
  form.value.fecha_entrada = formatDate(saturday)
  form.value.fecha_salida = formatDate(sunday)
}

let searchTimeout = null

const onCustomerInput = () => {
  // Show dropdown immediately when typing
  if (customerSearch.value.length >= 2) {
    showDropdown.value = true
  } else {
    showDropdown.value = false
    filteredCustomers.value = []
    return
  }
  
  // Clear previous timeout
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // Debounce search
  searchTimeout = setTimeout(async () => {
    isLoadingCustomers.value = true
    try {
      const result = await call('hermes.api.search_customers', {
        search: customerSearch.value
      })
      filteredCustomers.value = result || []
    } catch (e) {
      console.error('Error searching customers:', e)
      filteredCustomers.value = []
    } finally {
      isLoadingCustomers.value = false
    }
  }, 300)
}

const selectCustomer = (customer) => {
  form.value.cliente = customer.name
  form.value.customer_name = customer.customer_name
  customerSearch.value = ''
  showDropdown.value = false
  filteredCustomers.value = []
}

const createNewCustomer = async () => {
  if (!customerSearch.value.trim()) return
  
  isCreatingCustomer.value = true
  
  try {
    const result = await call('hermes.api.create_customer', {
      customer_name: customerSearch.value.trim()
    })
    
    if (result && result.name) {
      form.value.cliente = result.name
      form.value.customer_name = result.customer_name
      customerSearch.value = ''
      showDropdown.value = false
      filteredCustomers.value = []
    }
  } catch (e) {
    console.error('Error creating customer:', e)
    alert('Error al crear el cliente: ' + (e.message || 'Error desconocido'))
  } finally {
    isCreatingCustomer.value = false
  }
}

const clearCustomer = () => {
  form.value.cliente = ''
  form.value.customer_name = ''
}

const updateRoomPrice = () => {
  const room = availableRooms.value.find(r => r.name === form.value.habitacion)
  form.value.precio_base = room ? room.precio_base : 0
}

const getRoomName = () => {
  const room = availableRooms.value.find(r => r.name === form.value.habitacion)
  return room ? room.full_name : ''
}

const saveReservation = async () => {
  if (!isFormValid.value) return
  
  saving.value = true
  
  try {
    await call('hermes.api.create_reservation', {
      cliente: form.value.cliente,
      fecha_entrada: form.value.fecha_entrada,
      fecha_salida: form.value.fecha_salida,
      habitacion: form.value.habitacion,
      precio_base: form.value.precio_base,
      estado_reserva: form.value.estado_reserva,
      notas: form.value.notas
    })
    
    // Reset form
    form.value = {
      cliente: '',
      customer_name: '',
      fecha_entrada: '',
      fecha_salida: '',
      habitacion: '',
      precio_base: 0,
      estado_reserva: 'TENTATIVO',
      notas: ''
    }
    
    // Go to availability
    router.push('/availability')
  } catch (e) {
    if (e.message === 'SESSION_EXPIRED') {
      router.push('/login')
      return
    }
    alert('Error al guardar la reserva: ' + (e.message || 'Error desconocido'))
  } finally {
    saving.value = false
  }
}

// Watch for date changes to reload available rooms
watch([() => form.value.fecha_entrada, () => form.value.fecha_salida], () => {
  if (form.value.fecha_entrada && form.value.fecha_salida) {
    loadAvailableRooms()
  } else {
    availableRooms.value = []
    form.value.habitacion = ''
    form.value.precio_base = 0
  }
})

onMounted(() => {
  // Rooms will be loaded when dates are set
})
</script>

<style scoped>
.reservations-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #f0f4f8;
  padding-bottom: 70px;
}

/* Header */
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

/* Form Content */
.form-content {
  flex: 1;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  overflow-x: hidden;
}

/* Form */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  background: white;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input:disabled {
  background: #f8fafc;
  color: #94a3b8;
  cursor: not-allowed;
}

/* Dates Section */
.dates-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dates-section > label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
}

.dates-inputs {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.date-field {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.date-input {
  width: 100%;
  padding: 0.4rem 0.35rem;
  font-size: 0.75rem;
  min-width: 0;
  box-sizing: border-box;
  max-width: 100%;
}

.date-separator {
  color: #94a3b8;
  font-size: 0.75rem;
  flex-shrink: 0;
  padding: 0 0.125rem;
}

.quick-dates {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 0.375rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.quick-btn:active {
  background: #cbd5e1;
}

.nights-info-inline {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  background: #eff6ff;
  border-radius: 6px;
  color: #1e40af;
  font-size: 0.75rem;
  font-weight: 600;
}

.no-rooms-message {
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: #fef3c7;
  border-radius: 8px;
  color: #92400e;
  font-size: 0.875rem;
  text-align: center;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

/* Customer Search */
.customer-search {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.customer-search .form-input {
  width: 100%;
  max-width: 100%;
  font-size: 16px; /* Prevents zoom on iOS */
}

.customer-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  margin-top: 4px;
  width: 100%;
  box-sizing: border-box;
}

.customer-option {
  padding: 0.625rem 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 0;
  overflow: hidden;
}

.customer-option:hover {
  background: #f8fafc;
}

.customer-option:last-child {
  border-bottom: none;
}

.customer-option-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  min-width: 0;
  overflow: hidden;
  flex: 1;
}

.customer-option-main span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.customer-icon {
  width: 16px;
  height: 16px;
  color: #64748b;
  flex-shrink: 0;
}

.customer-label {
  font-size: 0.625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 9999px;
  background: #f1f5f9;
  color: #64748b;
  flex-shrink: 0;
}

.customer-label.new {
  background: #dcfce7;
  color: #16a34a;
}

.customer-option.create-new {
  background: #f0f9ff;
}

.customer-option.create-new:hover {
  background: #e0f2fe;
}

.customer-option.no-results {
  background: #f8fafc;
  justify-content: center;
  color: #94a3b8;
  font-size: 0.875rem;
}

.customer-option.loading {
  background: #f8fafc;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
}

.selected-customer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: #dcfce7;
  border-radius: 8px;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #166534;
  min-width: 0;
  overflow: hidden;
}

.selected-customer span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.clear-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #166534;
}

.clear-btn svg {
  width: 16px;
  height: 16px;
}

/* Price Card */
.price-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: #475569;
  padding: 0.5rem 0;
}

.price-row.total {
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 2px solid #e2e8f0;
  font-weight: 700;
  font-size: 1rem;
  color: #1e293b;
}

/* Save Button */
.save-btn {
  width: 100%;
  padding: 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: auto;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.btn-spinner.small {
  width: 14px;
  height: 14px;
  border-width: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
