<template>
  <div class="app-container">
    <router-view v-slot="{ Component, route }">
      <transition :name="transitionName" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const transitionName = ref('fade')

// Determine transition based on route depth
watch(
  () => route.path,
  (to, from) => {
    // Use slide transition for navigation between main views
    const mainViews = ['/availability', '/reservations', '/reports']
    const fromIndex = mainViews.indexOf(from)
    const toIndex = mainViews.indexOf(to)
    
    if (fromIndex !== -1 && toIndex !== -1) {
      // Slide left/right for main navigation
      transitionName.value = toIndex > fromIndex ? 'slide-left' : 'slide-right'
    } else {
      // Fade for other transitions
      transitionName.value = 'fade'
    }
  }
)
</script>

<style>
.app-container {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-background);
  overflow: visible !important;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 200ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide left transition */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 250ms ease, opacity 200ms ease;
}

.slide-left-enter-from {
  transform: translateX(30px);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(-30px);
  opacity: 0;
}

/* Slide right transition */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 250ms ease, opacity 200ms ease;
}

.slide-right-enter-from {
  transform: translateX(-30px);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(30px);
  opacity: 0;
}
</style>
