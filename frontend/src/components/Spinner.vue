<template>
  <div class="spinner" :class="sizeClass"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const sizeClass = computed(() => `spinner-${props.size}`)
</script>

<style scoped>
.spinner {
  border: 3px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-sm {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.spinner-md {
  width: 40px;
  height: 40px;
}

.spinner-lg {
  width: 64px;
  height: 64px;
  border-width: 4px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>