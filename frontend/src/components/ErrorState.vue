<template>
  <div class="error-state">
    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
    <p>{{ message }}</p>
    <button v-if="retry" class="retry-btn" @click="retry">{{ t('common.retry') }}</button>
  </div>
</template>

<script setup>
import { useI18n } from '../composables/useI18n'

defineProps({
  message: {
    type: String,
    default: 'Ha ocurrido un error'
  },
  retry: {
    type: Function,
    default: null
  }
})

const { t } = useI18n()
</script>

<style scoped>
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

.error-state svg {
  width: 48px;
  height: 48px;
  color: #ef4444;
  margin-bottom: 1rem;
}

.error-state p {
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.retry-btn:hover {
  background: #2563eb;
}
</style>