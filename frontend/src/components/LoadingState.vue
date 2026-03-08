<template>
  <div class="loading-state">
    <Spinner :size="size" />
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
import Spinner from './Spinner.vue'

defineProps({
  message: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md'
  }
})
</script>

<style scoped>
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
  font-size: 0.875rem;
}
</style>