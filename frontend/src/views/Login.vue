<template>
  <div class="login-container">
    <div class="login-header-section">
      <div class="logo-container">
        <svg class="logo-icon" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="32" cy="32" r="30" stroke="currentColor" stroke-width="2"/>
          <path d="M20 32L32 20L44 32L32 44L20 32Z" fill="currentColor"/>
          <circle cx="32" cy="32" r="8" fill="white"/>
        </svg>
      </div>
      <h1 class="brand-title">Hermes</h1>
      <p class="brand-subtitle">Sistema de Gestión Empresarial</p>
    </div>
    
    <div class="login-card">
      <div class="login-header">
        <h2 class="login-title">Iniciar Sesión</h2>
        <p class="login-subtitle">Ingresa tus credenciales para continuar</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email" class="form-label">Usuario</label>
          <div class="input-wrapper">
            <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <input
              id="email"
              v-model="email"
              type="text"
              required
              class="form-input"
              placeholder="Ingresa tu usuario"
              autocomplete="username"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Contraseña</label>
          <div class="input-wrapper">
            <svg class="input-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="form-input"
              placeholder="Ingresa tu contraseña"
              autocomplete="current-password"
            />
          </div>
        </div>

        <div class="form-options">
          <label class="checkbox-wrapper">
            <input type="checkbox" class="checkbox-input" v-model="rememberMe" />
            <span class="checkbox-label">Recordarme</span>
          </label>
          <a href="#" class="forgot-link">¿Olvidaste tu contraseña?</a>
        </div>

        <div v-if="error" class="error-message">
          <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="submit-btn"
        >
          <Spinner v-if="loading" size="sm" />
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>

      <div class="login-footer">
        <p class="footer-text">© 2026 Hermes</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../utils/frappe.js'
import { useI18n } from '../composables/useI18n'
import Spinner from '../components/Spinner.vue'

const router = useRouter()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const result = await login(email.value, password.value)
    
    if (result.success) {
      localStorage.setItem('hermes_token', result.token)
      localStorage.setItem('hermes_user', result.user)
      router.push('/availability')
    } else {
      error.value = result.message || 'Credenciales inválidas'
    }
  } catch (e) {
    error.value = 'Error de conexión. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #1e3a5f 0%, #0d1b2a 100%);
  padding: 0;
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
}

.login-header-section {
  padding: 2.5rem 1.5rem 1.5rem;
  text-align: center;
  background: linear-gradient(180deg, rgba(30, 58, 95, 0.9) 0%, rgba(13, 27, 42, 0.95) 100%);
  position: relative;
  overflow: hidden;
}

.login-header-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 50%);
  animation: pulse 15s infinite;
  pointer-events: none;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.3; }
}

.logo-container {
  margin-bottom: 0.75rem;
  position: relative;
  z-index: 1;
}

.logo-icon {
  width: 64px;
  height: 64px;
  color: #60a5fa;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.brand-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  background: linear-gradient(135deg, #fff 0%, #60a5fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
  z-index: 1;
}

.brand-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  position: relative;
  z-index: 1;
}

.login-card {
  flex: 1;
  background: #ffffff;
  border-radius: 24px 24px 0 0;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.login-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.login-subtitle {
  color: #64748b;
  font-size: 0.875rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9ca3af;
  pointer-events: none;
}

.form-input {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  color: #1f2937;
  transition: all 0.2s ease;
  background: #f9fafb;
  -webkit-appearance: none;
  appearance: none;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder {
  color: #9ca3af;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-input {
  width: 20px;
  height: 20px;
  accent-color: #3b82f6;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.forgot-link {
  font-size: 0.875rem;
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-link:active {
  color: #2563eb;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #dc2626;
  font-size: 0.875rem;
}

.error-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.submit-btn {
  width: 100%;
  padding: 1.125rem;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  min-height: 52px;
  -webkit-tap-highlight-color: transparent;
}

.submit-btn:active:not(:disabled) {
  transform: scale(0.98);
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.login-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  text-align: center;
}

.footer-text {
  font-size: 0.75rem;
  color: #9ca3af;
}

@supports (padding-top: env(safe-area-inset-top)) {
  .login-header-section {
    padding-top: calc(2.5rem + env(safe-area-inset-top));
  }
  
  .login-container {
    padding-bottom: env(safe-area-inset-bottom);
  }
}

@media (max-width: 360px) {
  .login-header-section {
    padding: 1.5rem 1rem 1rem;
  }
  
  .logo-icon {
    width: 56px;
    height: 56px;
  }
  
  .brand-title {
    font-size: 1.75rem;
  }
  
  .login-card {
    padding: 1.25rem;
  }
  
  .form-input {
    padding: 0.875rem 0.875rem 0.875rem 2.75rem;
  }
}

@media (orientation: landscape) and (max-height: 500px) {
  .login-container {
    flex-direction: row;
    overflow-y: auto;
  }
  
  .login-header-section {
    flex: 0 0 auto;
    min-width: 200px;
    padding: 1rem;
    border-radius: 0;
  }
  
  .logo-icon {
    width: 48px;
    height: 48px;
  }
  
  .brand-title {
    font-size: 1.5rem;
  }
  
  .brand-subtitle {
    display: none;
  }
  
  .login-card {
    flex: 1;
    border-radius: 0;
    padding: 1rem;
    justify-content: center;
  }
  
  .login-form {
    max-width: 400px;
    margin: 0 auto;
    width: 100%;
  }
}

@media (prefers-color-scheme: dark) {
  .login-card {
    background: #1e293b;
  }
  
  .login-title {
    color: #f1f5f9;
  }
  
  .login-subtitle {
    color: #94a3b8;
  }
  
  .form-label {
    color: #e2e8f0;
  }
  
  .form-input {
    background: #334155;
    border-color: #475569;
    color: #f1f5f9;
  }
  
  .form-input:focus {
    background: #334155;
    border-color: #3b82f6;
  }
  
  .form-input::placeholder {
    color: #94a3b8;
  }
  
  .checkbox-label {
    color: #cbd5e1;
  }
}
</style>
