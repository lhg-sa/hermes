<template>
  <nav class="bottom-nav">
    <router-link to="/availability" class="nav-item" :class="{ active: active === 'availability' }">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <span>{{ t('nav.availability') }}</span>
    </router-link>
    <router-link to="/reservations" class="nav-item" :class="{ active: active === 'reservations' }">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
      </svg>
      <span>{{ t('nav.new') }}</span>
    </router-link>
    <router-link to="/reports" class="nav-item" :class="{ active: active === 'reports' }">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
      </svg>
      <span>{{ t('nav.reports') }}</span>
    </router-link>
    <button class="nav-item" @click="handleLogout">
      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
      </svg>
      <span>{{ t('nav.logout') }}</span>
    </button>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'

defineProps({
  active: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const { t } = useI18n()
const { logout } = useAuth()

const handleLogout = async () => {
  await logout()
  router.push('/login')
}
</script>

<style scoped>
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