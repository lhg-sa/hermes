import { ref } from 'vue'

const translations = {
  // Navigation
  'nav.availability': 'Disponibilidad',
  'nav.reservations': 'Reservaciones',
  'nav.new': 'Reservar',
  'nav.reports': 'Reportes',
  'nav.logout': 'Cerrar Sesión',
  
  // Common
  'common.loading': 'Cargando...',
  'common.error': 'Ha ocurrido un error',
  'common.retry': 'Reintentar',
  'common.save': 'Guardar',
  'common.cancel': 'Cancelar',
  'common.delete': 'Eliminar',
  'common.edit': 'Editar',
  'common.back': 'Volver',
  'common.confirm': 'Confirmar',
  'common.search': 'Buscar',
  'common.noResults': 'Sin resultados',
  'common.required': 'Este campo es requerido',
  
  // Availability
  'availability.title': 'Disponibilidad de Habitaciones',
  'availability.loading': 'Cargando disponibilidad...',
  'availability.currentWeek': 'Semana Actual',
  'availability.today': 'Hoy',
  'availability.tomorrow': 'Mañana',
  'availability.weekend': 'Fin de semana',
  'availability.room': 'Habitación',
  'availability.status': 'Estado',
  'availability.available': 'Disponible',
  'availability.occupied': 'Ocupada',
  'availability.reserved': 'Reservada',
  'availability.selectMonthYear': 'Seleccionar Mes y Año',
  'availability.year': 'Año',
  'availability.month': 'Mes',
  'availability.rooms': 'HABITACIONES',
  'availability.showTotals': 'Mostrar Totales',
  'availability.hideTotals': 'Ocultar Totales',
  'availability.legend.tentative': 'Tentativo',
  'availability.legend.unpaid': 'Sin Pago',
  'availability.legend.paid': 'Pagada',
  'availability.legend.noshow': 'No Show',
  'availability.legend.free': 'Libre',
  
  // Months
  'months.january': 'Enero',
  'months.february': 'Febrero',
  'months.march': 'Marzo',
  'months.april': 'Abril',
  'months.may': 'Mayo',
  'months.june': 'Junio',
  'months.july': 'Julio',
  'months.august': 'Agosto',
  'months.september': 'Septiembre',
  'months.october': 'Octubre',
  'months.november': 'Noviembre',
  'months.december': 'Diciembre',
  
  // Reservations
  'reservations.title': 'Nueva Reservación',
  'reservations.customer': 'Cliente',
  'reservations.selectCustomer': 'Seleccionar cliente',
  'reservations.createNew': 'Crear nuevo',
  'reservations.checkIn': 'Entrada',
  'reservations.checkOut': 'Salida',
  'reservations.room': 'Habitación',
  'reservations.selectRoom': 'Seleccionar habitación',
  'reservations.price': 'Precio',
  'reservations.total': 'Total',
  'reservations.status': 'Estado',
  'reservations.notes': 'Notas',
  'reservations.create': 'Crear Reservación',
  'reservations.success': 'Reservación creada exitosamente',
  'reservations.error': 'Error al crear la reservación',
  
  // Reservation Detail
  'reservationDetail.title': 'Detalle de Reservación',
  'reservationDetail.customer': 'Cliente',
  'reservationDetail.dates': 'Fechas',
  'reservationDetail.room': 'Habitación',
  'reservationDetail.total': 'Total',
  'reservationDetail.paid': 'Pagado',
  'reservationDetail.pending': 'Pendiente',
  'reservationDetail.status': 'Estado',
  'reservationDetail.notes': 'Notas',
  'reservationDetail.createdAt': 'Creada',
  
  // Login
  'login.title': 'Iniciar Sesión',
  'login.username': 'Usuario',
  'login.password': 'Contraseña',
  'login.submit': 'Entrar',
  'login.error': 'Credenciales inválidas',
  
  // Status
  'status.confirmed': 'Confirmada',
  'status.pending': 'Pendiente',
  'status.cancelled': 'Cancelada',
  'status.checkedIn': 'Check-in',
  'status.checkedOut': 'Check-out'
}

const locale = ref('es')

export function useI18n() {
  function t(key, fallback = '') {
    const translation = translations[key]
    if (translation) {
      return translation
    }
    if (fallback) {
      return fallback
    }
    // Return key as fallback for missing translations
    return key
  }
  
  function setLocale(newLocale) {
    locale.value = newLocale
  }
  
  function getLocale() {
    return locale.value
  }
  
  return {
    t,
    locale,
    setLocale,
    getLocale
  }
}