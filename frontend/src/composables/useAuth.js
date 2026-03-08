import { ref } from 'vue'
import { useRouter } from 'vue-router'

const user = ref(null)
const isAuthenticated = ref(false)

export function useAuth() {
  const router = useRouter()
  
  async function logout() {
    try {
      // Call logout API
      await fetch('/api/method/logout', {
        method: 'POST',
        credentials: 'include'
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear local state regardless of API result
      user.value = null
      isAuthenticated.value = false
      
      // Redirect to login
      router.push('/login')
    }
  }
  
  async function checkAuth() {
    try {
      const response = await fetch('/api/method/frappe.auth.get_logged_user', {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        user.value = data.message
        isAuthenticated.value = !!data.message
        return true
      }
    } catch (error) {
      console.error('Auth check error:', error)
    }
    
    isAuthenticated.value = false
    user.value = null
    return false
  }
  
  async function login(username, password) {
    try {
      const response = await fetch('/api/method/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `usr=${encodeURIComponent(username)}&pwd=${encodeURIComponent(password)}`,
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        user.value = data.full_name || username
        isAuthenticated.value = true
        return { success: true }
      }
      
      return { success: false, error: 'Credenciales inválidas' }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: 'Error de conexión' }
    }
  }
  
  return {
    user,
    isAuthenticated,
    login,
    logout,
    checkAuth
  }
}