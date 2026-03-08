import { useI18n } from './useI18n'

export function useFormatters() {
  const { getLocale } = useI18n()
  
  /**
   * Format a number with locale-specific formatting
   */
  function formatNumber(value, decimals = 0) {
    if (value === null || value === undefined || isNaN(value)) {
      return '0'
    }
    
    const locale = getLocale() || 'es'
    const num = Number(value)
    
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num)
  }
  
  /**
   * Format a currency value with symbol
   */
  function formatCurrency(value, currency = 'GTQ', decimals = 2) {
    if (value === null || value === undefined || isNaN(value)) {
      return 'Q 0.00'
    }
    
    const locale = getLocale() || 'es'
    const num = Number(value)
    
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(num)
  }
  
  /**
   * Format a date with locale-specific formatting
   */
  function formatDate(value, options = {}) {
    if (!value) return ''
    
    const locale = getLocale() || 'es'
    const date = value instanceof Date ? value : new Date(value)
    
    if (isNaN(date.getTime())) return ''
    
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }
    
    return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options }).format(date)
  }
  
  /**
   * Format a date with time
   */
  function formatDateTime(value, options = {}) {
    if (!value) return ''
    
    const locale = getLocale() || 'es'
    const date = value instanceof Date ? value : new Date(value)
    
    if (isNaN(date.getTime())) return ''
    
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }
    
    return new Intl.DateTimeFormat(locale, { ...defaultOptions, ...options }).format(date)
  }
  
  /**
   * Format a date for input fields (YYYY-MM-DD)
   */
  function formatDateForInput(value) {
    if (!value) return ''
    
    const date = value instanceof Date ? value : new Date(value)
    if (isNaN(date.getTime())) return ''
    
    // Use Guatemala timezone to avoid date shifts
    const guatemalaDate = new Date(date.toLocaleString('en-US', { timeZone: 'America/Guatemala' }))
    const year = guatemalaDate.getFullYear()
    const month = String(guatemalaDate.getMonth() + 1).padStart(2, '0')
    const day = String(guatemalaDate.getDate()).padStart(2, '0')
    
    return `${year}-${month}-${day}`
  }
  
  /**
   * Format relative time (e.g., "hace 2 horas")
   */
  function formatRelativeTime(value) {
    if (!value) return ''
    
    const locale = getLocale() || 'es'
    const date = value instanceof Date ? value : new Date(value)
    
    if (isNaN(date.getTime())) return ''
    
    const now = new Date()
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
    
    if (diffInSeconds < 60) {
      return rtf.format(-diffInSeconds, 'second')
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return rtf.format(-minutes, 'minute')
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return rtf.format(-hours, 'hour')
    } else {
      const days = Math.floor(diffInSeconds / 86400)
      return rtf.format(-days, 'day')
    }
  }
  
  return {
    formatNumber,
    formatCurrency,
    formatDate,
    formatDateTime,
    formatDateForInput,
    formatRelativeTime
  }
}